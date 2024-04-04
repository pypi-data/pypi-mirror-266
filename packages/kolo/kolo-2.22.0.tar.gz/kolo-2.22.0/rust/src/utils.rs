use pyo3::exceptions::PyAttributeError;
use pyo3::exceptions::PyKeyError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyFrame;
use pyo3::types::PyTuple;
use pyo3::types::PyType;
use std::env::current_dir;
use std::path::Path;
use std::time::SystemTime;
use ulid::Ulid;

pub type SerializedFrame = Vec<u8>;

pub fn timestamp() -> f64 {
    SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .expect("System time is before unix epoch")
        .as_secs_f64()
}

pub fn frame_id() -> String {
    let frame_ulid = Ulid::new();
    format!("frm_{}", frame_ulid.to_string())
}

pub fn filename_with_lineno(
    frame: &Bound<'_, PyFrame>,
    py: Python,
) -> Result<(String, usize), PyErr> {
    let f_code = frame.getattr(intern!(py, "f_code"))?;
    let co_filename = f_code.getattr(intern!(py, "co_filename"))?;
    let filename = co_filename.extract::<String>()?;
    let lineno = frame.getattr(intern!(py, "f_lineno"))?;
    let lineno = lineno.extract()?;
    Ok((filename, lineno))
}

fn format_frame_path(filename: &str, lineno: usize) -> String {
    let path = match Path::new(filename).canonicalize() {
        Ok(path) => path,
        Err(_) => return format!("{}:{}", filename, lineno),
    };
    let dir = current_dir()
        .expect("Current directory is invalid")
        .canonicalize()
        .expect("Current directory cannot be canonicalized");
    let relative_path = match path.strip_prefix(&dir) {
        Ok(relative_path) => relative_path,
        Err(_) => &path,
    };
    format!("{}:{}", relative_path.display(), lineno)
}

pub fn frame_path(frame: &Bound<'_, PyFrame>, py: Python) -> Result<String, PyErr> {
    let (filename, lineno) = filename_with_lineno(frame, py)?;
    Ok(format_frame_path(&filename, lineno))
}

pub fn get_qualname(frame: &Bound<'_, PyFrame>, py: Python) -> Result<Option<String>, PyErr> {
    let f_code = frame.getattr(intern!(py, "f_code"))?;
    match f_code.getattr(intern!(py, "co_qualname")) {
        Ok(qualname) => {
            let globals = frame.getattr(intern!(py, "f_globals"))?;
            let module = globals.get_item("__name__")?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Err(err) if err.is_instance_of::<PyAttributeError>(py) => {}
        Err(err) => return Err(err),
    }

    let co_name = f_code.getattr(intern!(py, "co_name"))?;
    let name = co_name.extract::<String>()?;
    if name.as_str() == "<module>" {
        let globals = frame.getattr(intern!(py, "f_globals"))?;
        let module = globals.get_item("__name__")?;
        return Ok(Some(format!("{}.<module>", module)));
    }

    match _get_qualname_inner(frame, py, &co_name) {
        Ok(qualname) => Ok(qualname),
        Err(_) => Ok(None),
    }
}

fn _get_qualname_inner(
    frame: &Bound<'_, PyFrame>,
    py: Python,
    co_name: &Bound<'_, PyAny>,
) -> Result<Option<String>, PyErr> {
    let outer_frame = frame.getattr(intern!(py, "f_back"))?;
    if outer_frame.is_none() {
        return Ok(None);
    }

    let outer_frame_locals = outer_frame.getattr(intern!(py, "f_locals"))?;
    match outer_frame_locals.get_item(co_name) {
        Ok(function) => {
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {}
        Err(_) => return Ok(None),
    }

    let locals = frame.getattr(intern!(py, "f_locals"))?;
    let inspect = PyModule::import_bound(py, "inspect")?;
    let getattr_static = inspect.getattr(intern!(py, "getattr_static"))?;
    match locals.get_item("self") {
        Ok(locals_self) => {
            let function = getattr_static.call1((locals_self, co_name))?;
            let builtins = py.import_bound("builtins")?;
            let property = builtins.getattr(intern!(py, "property"))?;
            let property = property.downcast()?;
            let function = match function.is_instance(property)? {
                true => function.getattr(intern!(py, "fget"))?,
                false => function,
            };
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {}
        Err(_) => return Ok(None),
    };

    match locals.get_item("cls") {
        Ok(cls) if cls.is_instance_of::<PyType>() => {
            let function = getattr_static.call1((cls, co_name))?;
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            return Ok(Some(format!("{}.{}", module, qualname)));
        }
        Ok(_) => {}
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {}
        Err(_) => return Ok(None),
    }
    let globals = frame.getattr(intern!(py, "f_globals"))?;
    match locals.get_item("__qualname__") {
        Ok(qualname) => {
            let module = globals.get_item("__name__")?;
            Ok(Some(format!("{}.{}", module, qualname)))
        }
        Err(err) if err.is_instance_of::<PyKeyError>(py) => {
            let function = globals.get_item(co_name)?;
            let module = function.getattr(intern!(py, "__module__"))?;
            let qualname = function.getattr(intern!(py, "__qualname__"))?;
            Ok(Some(format!("{}.{}", module, qualname)))
        }
        Err(_) => Ok(None),
    }
}

pub fn dump_msgpack(py: Python, data: &Bound<'_, PyAny>) -> Result<Vec<u8>, PyErr> {
    let serialize = PyModule::import_bound(py, "kolo.serialize")?;
    let args = PyTuple::new_bound(py, [&data]);
    let data = serialize.call_method1("dump_msgpack", args)?;
    data.extract::<Vec<u8>>()
}

pub fn write_str_pair(buf: &mut Vec<u8>, key: &str, value: Option<&str>) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    match value {
        Some(value) => rmp::encode::write_str(buf, value).expect("Writing to memory, not I/O"),
        None => rmp::encode::write_nil(buf).expect("Writing to memory, not I/O"),
    };
}

pub fn write_raw_pair(buf: &mut Vec<u8>, key: &str, value: &mut Vec<u8>) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    buf.append(value);
}

pub fn write_int_pair(buf: &mut Vec<u8>, key: &str, value: usize) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    rmp::encode::write_uint(buf, value as u64).expect("Writing to memory, not I/O");
}

pub fn write_f64_pair(buf: &mut Vec<u8>, key: &str, value: f64) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    rmp::encode::write_f64(buf, value).expect("Writing to memory, not I/O");
}

pub fn write_bool_pair(buf: &mut Vec<u8>, key: &str, value: bool) {
    rmp::encode::write_str(buf, key).expect("Writing to memory, not I/O");
    rmp::encode::write_bool(buf, value).expect("Writing to memory, not I/O");
}

pub fn write_raw_frames(buf: &mut Vec<u8>, frames: Vec<SerializedFrame>) {
    rmp::encode::write_array_len(buf, frames.len() as u32).expect("Writing to memory, not I/O");
    buf.append(&mut frames.into_iter().flatten().collect());
}

pub fn current_thread(py: Python) -> Result<(String, usize), PyErr> {
    let threading = PyModule::import_bound(py, "threading")?;
    let thread = threading.call_method0("current_thread")?;
    let thread_name = thread.getattr(intern!(py, "name"))?;
    let thread_name = thread_name.extract()?;
    let native_id = thread.getattr(intern!(py, "native_id"))?;
    let native_id = native_id.extract()?;
    Ok((thread_name, native_id))
}

pub struct UserCodeCallSite {
    pub call_frame_id: String,
    pub line_number: i32,
}

pub fn user_code_call_site(
    py: Python,
    call_frames: Vec<(PyObject, String)>,
    frame_id: Option<&str>,
) -> Result<Option<UserCodeCallSite>, PyErr> {
    let frame_id = match frame_id {
        Some(frame_id) => frame_id,
        None => {
            return Ok(None);
        }
    };

    let (call_frame, call_frame_id) = match call_frames
        .iter()
        .rev()
        .take(2)
        .find(|(_f, f_id)| f_id != frame_id)
    {
        Some(frame_data) => frame_data,
        None => {
            return Ok(None);
        }
    };

    let pyframe = call_frame.downcast_bound::<PyFrame>(py)?;
    Ok(Some(UserCodeCallSite {
        call_frame_id: call_frame_id.to_string(),
        line_number: pyframe.getattr(intern!(py, "f_lineno"))?.extract()?,
    }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_frame_path_invalid_path() {
        let frame_path = format_frame_path("<module>", 23);

        assert_eq!(frame_path, "<module>:23");
    }
}
