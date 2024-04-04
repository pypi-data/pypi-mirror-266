use bstr::Finder;
use pyo3::ffi;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::types::PyDict;
use pyo3::types::PyFrame;
use std::cell::RefCell;
use std::collections::HashMap;
use std::os::raw::c_int;
use std::sync::Mutex;
use thread_local::ThreadLocal;
use ulid::Ulid;

use super::filters;
use super::plugins::{load_plugins, PluginProcessor};
use super::utils;
use super::utils::SerializedFrame;

#[pyclass(module = "kolo._kolo")]
pub struct KoloProfiler {
    db_path: String,
    one_trace_per_test: bool,
    trace_id: Mutex<String>,
    frames_of_interest: Mutex<Vec<SerializedFrame>>,
    frames: Mutex<HashMap<usize, Vec<SerializedFrame>>>,
    include_frames: Vec<Finder<'static>>,
    ignore_frames: Vec<Finder<'static>>,
    default_include_frames: HashMap<String, Vec<PluginProcessor>>,
    call_frames: ThreadLocal<RefCell<Vec<(PyObject, String)>>>,
    timestamp: f64,
    _frame_ids: ThreadLocal<RefCell<HashMap<usize, String>>>,
    main_thread_id: usize,
    source: String,
    timeout: usize,
    use_threading: bool,
}

#[pymethods]
impl KoloProfiler {
    fn save_request_in_db(&self) -> Result<(), PyErr> {
        Python::with_gil(|py| self.save_in_db(py))
    }

    fn build_trace(&self) -> Result<Py<PyBytes>, PyErr> {
        Python::with_gil(|py| self.build_trace_inner(py))
    }

    fn register_threading_profiler(
        slf: PyRef<'_, Self>,
        _frame: PyObject,
        _event: PyObject,
        _arg: PyObject,
    ) -> Result<(), PyErr> {
        // Safety:
        //
        // PyEval_SetProfile takes two arguments:
        //  * trace_func: Option<Py_tracefunc>
        //  * arg1:       *mut PyObject
        //
        // `profile_callback` matches the signature of a `Py_tracefunc`, so we only
        // need to wrap it in `Some`.
        // `slf.into_ptr()` is a pointer to our Rust profiler instance as a Python
        // object.
        //
        // We must also hold the GIL, which we do because we're called from python.
        //
        // https://docs.rs/pyo3-ffi/latest/pyo3_ffi/fn.PyEval_SetProfile.html
        // https://docs.python.org/3/c-api/init.html#c.PyEval_SetProfile
        unsafe {
            ffi::PyEval_SetProfile(Some(profile_callback), slf.into_ptr());
        }
        Ok(())
    }
}

impl KoloProfiler {
    pub fn new_from_python(py: Python, py_profiler: &Bound<'_, PyAny>) -> Result<Self, PyErr> {
        let config = py_profiler.getattr(intern!(py, "config"))?;
        let config = config.downcast::<PyDict>()?;
        let filters = config
            .get_item("filters")
            .expect("config.get(\"filters\" should not raise.");
        let include_frames = match &filters {
            Some(filters) => match filters.get_item("include_frames") {
                Ok(include_frames) => include_frames
                    .extract::<Vec<String>>()?
                    .iter()
                    .map(Finder::new)
                    .map(|finder| finder.into_owned())
                    .collect(),
                Err(_) => Vec::new(),
            },
            None => Vec::new(),
        };
        let ignore_frames = match &filters {
            Some(filters) => match filters.get_item("ignore_frames") {
                Ok(ignore_frames) => ignore_frames
                    .extract::<Vec<String>>()?
                    .iter()
                    .map(Finder::new)
                    .map(|finder| finder.into_owned())
                    .collect(),
                Err(_) => Vec::new(),
            },
            None => Vec::new(),
        };
        let threading = PyModule::import_bound(py, "threading")?;
        let main_thread = threading.call_method0(intern!(py, "main_thread"))?;
        let main_thread_id = main_thread.getattr(intern!(py, "native_id"))?;
        let main_thread_id = main_thread_id.extract()?;
        let timeout = match config
            .get_item("sqlite_busy_timeout")
            .expect("config.get(\"sqlite_busy_timeout\" should not raise.")
        {
            Some(timeout) => timeout.extract()?,
            None => 60,
        };
        let use_threading = match config
            .get_item("threading")
            .expect("config.get(\"threading\" should not raise.")
        {
            Some(threading) => threading.extract::<bool>().unwrap_or(false),
            None => false,
        };

        let default_include_frames = load_plugins(py, config)?;
        Ok(Self {
            db_path: py_profiler
                .getattr(intern!(py, "db_path"))?
                .str()?
                .extract()?,
            one_trace_per_test: py_profiler
                .getattr(intern!(py, "one_trace_per_test"))?
                .extract()?,
            trace_id: py_profiler
                .getattr(intern!(py, "trace_id"))?
                .extract::<String>()?
                .into(),
            source: py_profiler
                .getattr(intern!(py, "source"))?
                .extract::<String>()?,
            frames: HashMap::new().into(),
            frames_of_interest: Vec::new().into(),
            include_frames,
            ignore_frames,
            default_include_frames,
            call_frames: ThreadLocal::new(),
            timestamp: utils::timestamp(),
            _frame_ids: ThreadLocal::new(),
            main_thread_id,
            timeout,
            use_threading,
        })
    }

    fn write_argv(&self, buf: &mut Vec<u8>, argv: Vec<String>) {
        rmp::encode::write_str(buf, "command_line_args").expect("Writing to memory, not I/O");
        rmp::encode::write_array_len(buf, argv.len() as u32).expect("Writing to memory, not I/O");
        for arg in argv {
            rmp::encode::write_str(buf, &arg).expect("Writing to memory, not I/O");
        }
    }

    fn write_frames(&self, buf: &mut Vec<u8>, frames: HashMap<usize, Vec<SerializedFrame>>) {
        rmp::encode::write_str(buf, "frames").expect("Writing to memory, not I/O");
        rmp::encode::write_map_len(buf, frames.len() as u32).expect("Writing to memory, not I/O");
        for (thread_id, frames) in frames {
            rmp::encode::write_uint(buf, thread_id as u64).expect("Writing to memory, not I/O");
            utils::write_raw_frames(buf, frames);
        }
    }

    fn write_frames_of_interest(
        &self,
        buf: &mut Vec<u8>,
        frames_of_interest: Vec<SerializedFrame>,
    ) {
        rmp::encode::write_str(buf, "frames_of_interest").expect("Writing to memory, not I/O");
        utils::write_raw_frames(buf, frames_of_interest);
    }

    fn write_meta(&self, buf: &mut Vec<u8>, version: &str, source: &str) {
        rmp::encode::write_str(buf, "meta").expect("Writing to memory, not I/O");
        rmp::encode::write_map_len(buf, 3).expect("Writing to memory, not I/O");

        utils::write_str_pair(buf, "version", Some(version));
        utils::write_str_pair(buf, "source", Some(source));
        utils::write_bool_pair(buf, "use_frame_boundaries", true);
    }

    fn build_trace_inner(&self, py: Python) -> Result<Py<PyBytes>, PyErr> {
        let version = PyModule::import_bound(py, "kolo.version")?
            .getattr(intern!(py, "__version__"))?
            .extract::<String>()?;
        let commit_sha = PyModule::import_bound(py, "kolo.git")?
            .getattr(intern!(py, "COMMIT_SHA"))?
            .extract::<Option<String>>()?;
        let argv = PyModule::import_bound(py, "sys")?
            .getattr(intern!(py, "argv"))?
            .extract::<Vec<String>>()?;
        let mut state = self.frames_of_interest.lock().unwrap();
        let frames_of_interest = std::mem::take(&mut *state);
        let mut state = self.frames.lock().unwrap();
        let frames = std::mem::take(&mut *state);

        let trace_id = self.trace_id.lock().unwrap().clone();
        let mut buf: Vec<u8> = vec![];

        rmp::encode::write_map_len(&mut buf, 8).expect("Writing to memory, not I/O");
        self.write_argv(&mut buf, argv);
        utils::write_str_pair(&mut buf, "current_commit_sha", commit_sha.as_deref());
        self.write_frames(&mut buf, frames);
        self.write_frames_of_interest(&mut buf, frames_of_interest);
        utils::write_int_pair(&mut buf, "main_thread_id", self.main_thread_id);
        self.write_meta(&mut buf, &version, &self.source);
        utils::write_f64_pair(&mut buf, "timestamp", self.timestamp);
        utils::write_str_pair(&mut buf, "trace_id", Some(&trace_id));

        Ok(PyBytes::new_bound(py, &buf).unbind())
    }

    fn save_in_db(&self, py: Python) -> Result<(), PyErr> {
        let kwargs = PyDict::new_bound(py);
        kwargs.set_item("timeout", self.timeout).unwrap();

        let data = self.build_trace_inner(py)?;
        kwargs.set_item("msgpack", data).unwrap();

        let trace_id = self.trace_id.lock().unwrap().clone();
        let db = PyModule::import_bound(py, "kolo.db")?;
        let save = db.getattr(intern!(py, "save_trace_in_sqlite"))?;
        save.call((&self.db_path, &trace_id), Some(&kwargs))?;
        Ok(())
    }

    fn process_frame(
        &self,
        frame: &PyObject,
        event: &str,
        arg: PyObject,
        py: Python,
    ) -> Result<(), PyErr> {
        let (thread_name, native_id) = utils::current_thread(py)?;
        let pyframe = frame.downcast_bound::<PyFrame>(py)?;
        let arg = arg.downcast_bound::<PyAny>(py)?;
        let f_code = pyframe.getattr(intern!(py, "f_code"))?;
        let co_name = f_code.getattr(intern!(py, "co_name"))?;
        let name = co_name.extract::<String>()?;
        let pyframe_id = pyframe.as_ptr() as usize;
        let path = utils::frame_path(pyframe, py)?;
        let qualname = utils::get_qualname(pyframe, py)?;
        let locals = pyframe.getattr(intern!(py, "f_locals"))?;
        let locals = locals.downcast_into::<PyDict>().unwrap();
        let locals = match locals
            .get_item("__builtins__")
            .expect("locals.get(\"__builtins__\") should not raise.")
        {
            Some(_) => {
                let locals = locals.copy().unwrap();
                locals.del_item("__builtins__").unwrap();
                locals
            }
            None => locals,
        };
        let frame_id = self.get_and_set_frame_id(event, pyframe_id);
        let user_code_call_site = match utils::user_code_call_site(
            py,
            self.call_frames.get_or_default().borrow().to_vec(),
            frame_id.as_deref(),
        )? {
            Some(user_code_call_site) => rmpv::Value::Map(vec![
                (
                    "call_frame_id".into(),
                    user_code_call_site.call_frame_id.into(),
                ),
                ("line_number".into(), user_code_call_site.line_number.into()),
            ]),
            None => rmpv::Value::Nil,
        };
        let mut arg = utils::dump_msgpack(py, arg)?;
        let mut locals = utils::dump_msgpack(py, &locals)?;

        self.update_call_frames(event, frame, frame_id.as_deref());

        let mut buf: Vec<u8> = vec![];

        rmp::encode::write_map_len(&mut buf, 12).expect("Writing to memory, not I/O");

        utils::write_str_pair(&mut buf, "path", Some(&path));
        utils::write_str_pair(&mut buf, "co_name", Some(&name));
        utils::write_str_pair(&mut buf, "qualname", qualname.as_deref());
        utils::write_str_pair(&mut buf, "event", Some(event));
        utils::write_str_pair(&mut buf, "frame_id", frame_id.as_deref());
        utils::write_raw_pair(&mut buf, "arg", &mut arg);
        utils::write_raw_pair(&mut buf, "locals", &mut locals);
        utils::write_str_pair(&mut buf, "thread", Some(&thread_name));
        utils::write_int_pair(&mut buf, "thread_native_id", native_id);
        utils::write_f64_pair(&mut buf, "timestamp", utils::timestamp());
        utils::write_str_pair(&mut buf, "type", Some("frame"));

        rmp::encode::write_str(&mut buf, "user_code_call_site")
            .expect("Writing to memory, not I/O");
        rmpv::encode::write_value(&mut buf, &user_code_call_site).unwrap();

        self.push_frame_data(py, buf)
    }

    fn get_and_set_frame_id(&self, event: &str, pyframe_id: usize) -> Option<String> {
        match event {
            "call" => {
                let frame_id = utils::frame_id();
                self._frame_ids
                    .get_or_default()
                    .borrow_mut()
                    .insert(pyframe_id, frame_id.clone());
                Some(frame_id)
            }
            "return" => self
                ._frame_ids
                .get_or_default()
                .borrow()
                .get(&pyframe_id)
                .cloned(),
            _ => None,
        }
    }

    fn update_call_frames(&self, event: &str, frame: &PyObject, frame_id: Option<&str>) {
        match (event, frame_id) {
            ("call", Some(frame_id)) => {
                self.call_frames
                    .get_or_default()
                    .borrow_mut()
                    .push((frame.clone(), frame_id.to_string()));
            }
            ("return", _) => {
                if let Some(e) = self.call_frames.get() {
                    e.borrow_mut().pop();
                }
            }
            _ => {}
        }
    }

    fn push_frame_data(&self, py: Python, data: SerializedFrame) -> Result<(), PyErr> {
        let (_, native_id) = utils::current_thread(py)?;
        if !self.use_threading || native_id == self.main_thread_id {
            self.frames_of_interest.lock().unwrap().push(data);
        } else {
            self.frames
                .lock()
                .unwrap()
                .entry(native_id)
                .or_default()
                .push(data);
        };
        Ok(())
    }

    fn process_include_frames(&self, filename: &str) -> bool {
        self.include_frames
            .iter()
            .any(|finder| finder.find(filename).is_some())
    }

    fn process_ignore_frames(&self, filename: &str) -> bool {
        self.ignore_frames
            .iter()
            .any(|finder| finder.find(filename).is_some())
    }

    fn process_default_ignore_frames(
        &self,
        pyframe: &Bound<'_, PyFrame>,
        co_filename: &str,
        py: Python,
    ) -> Result<bool, PyErr> {
        if filters::library_filter(co_filename) {
            return Ok(true);
        }

        if filters::frozen_filter(co_filename) {
            return Ok(true);
        }

        if filters::kolo_filter(co_filename) {
            return Ok(true);
        }

        if filters::exec_filter(co_filename) {
            return Ok(true);
        }

        if filters::attrs_filter(co_filename, pyframe, py)? {
            return Ok(true);
        }

        Ok(filters::pytest_generated_filter(co_filename, pyframe, py))
    }

    fn process_default_include_frames(
        &mut self,
        py: Python,
        frame: &PyObject,
        event: &str,
        arg: &PyObject,
        name: &str,
        filename: &str,
    ) -> Result<bool, PyErr> {
        let filters = match self.default_include_frames.get_mut(name) {
            Some(filters) => filters,
            None => {
                return Ok(false);
            }
        };
        let frame = frame.bind(py);
        for filter in filters.iter_mut() {
            match filter.matches(py, frame, event, arg, filename)? {
                true => {
                    let pyframe = frame.downcast::<PyFrame>()?;
                    let data = filter.process(
                        py,
                        pyframe,
                        event,
                        arg,
                        self.call_frames.get_or_default().borrow().clone(),
                    )?;
                    let frame_type = data
                        .bind(py)
                        .get_item("type")
                        .expect("data.get(\"type\" should not raise.");
                    let frame_type = match frame_type {
                        Some(ref frame_type) => frame_type.extract()?,
                        None => "",
                    };
                    if self.one_trace_per_test && frame_type == "start_test" {
                        let trace_id = Ulid::new();
                        let trace_id = format!("trc_{}", trace_id.to_string());
                        let mut self_trace_id = self.trace_id.lock().unwrap();
                        *self_trace_id = trace_id;

                        let mut frames_of_interest = self.frames_of_interest.lock().unwrap();
                        *frames_of_interest = vec![];
                        let mut frames = self.frames.lock().unwrap();
                        *frames = HashMap::new();
                    }

                    let data = utils::dump_msgpack(py, data.bind(py))?;
                    self.push_frame_data(py, data)?;

                    if self.one_trace_per_test && frame_type == "end_test" {
                        self.save_in_db(py)?;
                    }
                    return Ok(true);
                }
                false => continue,
            }
        }
        Ok(false)
    }

    fn profile(
        &mut self,
        frame: &PyObject,
        arg: PyObject,
        event: &str,
        py: Python,
    ) -> Result<(), PyErr> {
        let pyframe = frame.bind(py);
        let pyframe = pyframe.downcast::<PyFrame>()?;
        let f_code = pyframe.getattr(intern!(py, "f_code"))?;
        let co_filename = f_code.getattr(intern!(py, "co_filename"))?;
        let filename = co_filename.extract::<String>()?;

        if self.process_include_frames(&filename) {
            self.process_frame(frame, event, arg, py)?;
            return Ok(());
        };

        if self.process_ignore_frames(&filename) {
            return Ok(());
        }

        let co_name = f_code.getattr(intern!(py, "co_name"))?;
        let name = co_name.extract::<String>()?;

        if self.process_default_include_frames(py, frame, event, &arg, &name, &filename)? {
            return Ok(());
        }

        if self.process_default_ignore_frames(pyframe, &filename, py)? {
            return Ok(());
        }

        self.process_frame(frame, event, arg, py)
    }
}

const PYTHON_EXCEPTION_WARNING: &str = "Unexpected exception in Rust.
    co_filename: %s
    co_name: %s
    frame locals: %s
";

// Safety:
//
// We match the type signature of `Py_tracefunc`.
//
// https://docs.rs/pyo3-ffi/latest/pyo3_ffi/type.Py_tracefunc.html
pub extern "C" fn profile_callback(
    _obj: *mut ffi::PyObject,
    _frame: *mut ffi::PyFrameObject,
    what: c_int,
    _arg: *mut ffi::PyObject,
) -> c_int {
    let event = match what {
        ffi::PyTrace_CALL => "call",
        ffi::PyTrace_RETURN => "return",
        _ => return 0,
    };
    let _frame = _frame as *mut ffi::PyObject;
    Python::with_gil(|py| {
        // Safety:
        //
        // `from_borrowed_ptr_or_err` must be called in an unsafe block.
        //
        // `_obj` is a reference to our `KoloProfiler` wrapped up in a Python object, so
        // we can safely convert it from an `ffi::PyObject` to a `PyObject`.
        //
        // We borrow the object so we don't break reference counting.
        //
        // https://docs.rs/pyo3/latest/pyo3/struct.Py.html#method.from_borrowed_ptr_or_err
        // https://docs.python.org/3/c-api/init.html#c.Py_tracefunc
        let obj = match unsafe { PyObject::from_borrowed_ptr_or_err(py, _obj) } {
            Ok(obj) => obj,
            Err(err) => {
                err.restore(py);
                return -1;
            }
        };
        let mut profiler = match obj.extract::<PyRefMut<KoloProfiler>>(py) {
            Ok(profiler) => profiler,
            Err(err) => {
                err.restore(py);
                return -1;
            }
        };

        // Safety:
        //
        // `from_borrowed_ptr_or_err` must be called in an unsafe block.
        //
        // `_frame` is an `ffi::PyFrameObject` which can be converted safely
        // to a `PyObject`. We can later convert it into a `pyo3::types::PyFrame`.
        //
        // We borrow the object so we don't break reference counting.
        //
        // https://docs.rs/pyo3/latest/pyo3/struct.Py.html#method.from_borrowed_ptr_or_err
        // https://docs.python.org/3/c-api/init.html#c.Py_tracefunc
        let frame = match unsafe { PyObject::from_borrowed_ptr_or_err(py, _frame) } {
            Ok(frame) => frame,
            Err(err) => {
                err.restore(py);
                return -1;
            }
        };

        // Safety:
        //
        // `from_borrowed_ptr_or_opt` must be called in an unsafe block.
        //
        // `_arg` is either a `Py_None` (PyTrace_CALL) or any PyObject (PyTrace_RETURN) or
        // NULL (PyTrace_RETURN). The first two can be unwrapped as a PyObject. `NULL` we
        // convert to a `py.None()`.
        //
        // We borrow the object so we don't break reference counting.
        //
        // https://docs.rs/pyo3/latest/pyo3/struct.Py.html#method.from_borrowed_ptr_or_opt
        // https://docs.python.org/3/c-api/init.html#c.Py_tracefunc
        let arg = match unsafe { PyObject::from_borrowed_ptr_or_opt(py, _arg) } {
            Some(arg) => arg,
            // TODO: Perhaps better exception handling here?
            None => py.None(),
        };

        match profiler.profile(&frame, arg, event, py) {
            Ok(_) => 0,
            Err(err) => {
                let logging = PyModule::import_bound(py, "logging").unwrap();
                let logger = logging.call_method1("getLogger", ("kolo",)).unwrap();

                let pyframe = frame.bind(py);
                let pyframe = pyframe.downcast::<PyFrame>().unwrap();
                let f_code = pyframe.getattr(intern!(py, "f_code")).unwrap();
                let co_filename = f_code.getattr(intern!(py, "co_filename")).unwrap();
                let co_name = f_code.getattr(intern!(py, "co_name")).unwrap();
                let locals = pyframe.getattr(intern!(py, "f_locals")).unwrap();

                let kwargs = PyDict::new_bound(py);
                kwargs.set_item("exc_info", err).unwrap();

                logger
                    .call_method(
                        "warning",
                        (PYTHON_EXCEPTION_WARNING, co_filename, co_name, locals),
                        Some(&kwargs),
                    )
                    .unwrap();
                0
            }
        }
    })
}
