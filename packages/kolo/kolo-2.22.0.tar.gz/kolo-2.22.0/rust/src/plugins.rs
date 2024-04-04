use bstr::Finder;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyFrame, PyList, PyModule};
use pyo3::{PyErr, Python};
use std::collections::HashMap;
use ulid::Ulid;

use super::utils;

#[derive(Debug)]
pub struct PluginProcessor {
    filename_finder: Finder<'static>,
    call_type: String,
    return_type: String,
    subtype: Option<String>,
    call: Option<PyObject>,
    process: Option<PyObject>,
    context: Py<PyDict>,
    frame_ids: HashMap<usize, String>,
}

impl PluginProcessor {
    fn new(plugin_data: &Bound<'_, PyDict>, context: &Bound<'_, PyDict>) -> Result<Self, PyErr> {
        let filename = plugin_data.as_any().get_item("path_fragment")?;
        let filename: &str = filename.extract()?;
        #[cfg(target_os = "windows")]
        let filename = filename.replace("/", "\\");
        let plugin = Self {
            filename_finder: Finder::new(&filename).into_owned(),
            call_type: plugin_data.as_any().get_item("call_type")?.extract()?,
            return_type: plugin_data.as_any().get_item("return_type")?.extract()?,
            subtype: match plugin_data
                .get_item("subtype")
                .expect("a string is always a valid dict key")
            {
                Some(subtype) => Some(subtype.extract()?),
                None => None,
            },
            call: match plugin_data
                .get_item("call")
                .expect("a string is always a valid dict key")
            {
                Some(call) => {
                    if call.is_none() {
                        None
                    } else {
                        Some(call.into())
                    }
                }
                None => None,
            },
            process: match plugin_data
                .get_item("process")
                .expect("a string is always a valid dict key")
            {
                Some(process) => {
                    if process.is_none() {
                        None
                    } else {
                        Some(process.into())
                    }
                }
                None => None,
            },
            // Cloning here is just bumping the reference count. This is what we want,
            // so Python knows we need `context` to continue to exist.
            context: context.clone().unbind(),
            frame_ids: HashMap::new(),
        };
        Ok(plugin)
    }

    pub fn matches(
        &self,
        py: Python,
        frame: &Bound<'_, PyAny>,
        event: &str,
        arg: &PyObject,
        filename: &str,
    ) -> Result<bool, PyErr> {
        let filename_matches = self.filename_finder.find(filename).is_some();
        match &self.call {
            None => Ok(filename_matches),
            Some(call) => Ok(filename_matches
                && call
                    .call1(py, (frame, event, arg, &self.context))?
                    .extract(py)?),
        }
    }

    fn frame_id(&mut self, pyframe: &Bound<'_, PyFrame>, event: &str) -> Option<String> {
        let pyframe_id = pyframe.as_ptr() as usize;
        match event {
            "call" => {
                let frame_id = Ulid::new();
                let frame_id = format!("frm_{}", frame_id.to_string());
                self.frame_ids.insert(pyframe_id, frame_id.clone());
                Some(frame_id)
            }
            "return" => match self.frame_ids.get(&pyframe_id) {
                Some(frame_id) => Some(frame_id.clone()),
                None => {
                    let frame_id = Ulid::new();
                    Some(format!("frm_{}", frame_id.to_string()))
                }
            },
            _ => None,
        }
    }

    pub fn process(
        &mut self,
        py: Python,
        pyframe: &Bound<'_, PyFrame>,
        event: &str,
        arg: &PyObject,
        call_frames: Vec<(PyObject, String)>,
    ) -> Result<Py<PyDict>, PyErr> {
        let data = PyDict::new_bound(py);
        let frame_id = self.frame_id(pyframe, event);
        data.set_item("frame_id", frame_id.clone())
            .expect("a string is always a valid dict key");
        data.set_item("timestamp", utils::timestamp())
            .expect("a string is always a valid dict key");
        let (thread_name, native_id) = utils::current_thread(py)?;
        data.set_item("thread", thread_name)
            .expect("a string is always a valid dict key");
        data.set_item("thread_native_id", native_id)
            .expect("a string is always a valid dict key");

        let call_site = match utils::user_code_call_site(py, call_frames, frame_id.as_deref())? {
            Some(user_code_call_site) => {
                let call_site = PyDict::new_bound(py);
                call_site
                    .set_item("call_frame_id", user_code_call_site.call_frame_id)
                    .expect("a string is always a valid dict key");
                call_site
                    .set_item("line_number", user_code_call_site.line_number)
                    .expect("a string is always a valid dict key");
                Some(call_site)
            }
            None => None,
        };
        data.set_item("user_code_call_site", call_site)
            .expect("a string is always a valid dict key");

        match event {
            "call" => data
                .set_item("type", &self.call_type)
                .expect("a string is always a valid dict key"),
            "return" => data
                .set_item("type", &self.return_type)
                .expect("a string is always a valid dict key"),
            _ => (),
        }
        if let Some(subtype) = &self.subtype {
            data.set_item("subtype", subtype)
                .expect("a string is always a valid dict key");
        }
        if let Some(process) = &self.process {
            data.update(
                process
                    .call1(py, (pyframe, event, arg, &self.context))?
                    .downcast_bound(py)?,
            )?;
        }
        Ok(data.into())
    }
}

fn load_plugin_data(
    py: Python,
    plugins: &Bound<'_, PyList>,
    config: &Bound<'_, PyDict>,
) -> Result<HashMap<String, Vec<PluginProcessor>>, PyErr> {
    let mut processors: HashMap<String, Vec<PluginProcessor>> =
        HashMap::with_capacity(plugins.len());

    for plugin_data in plugins {
        let plugin_data: &Bound<'_, PyDict> = plugin_data.downcast()?;
        let co_names = plugin_data.as_any().get_item("co_names")?;
        let context = match plugin_data
            .get_item("build_context")
            .expect("a string is always a valid dict key")
        {
            Some(build_context) => {
                if build_context.is_none() {
                    PyDict::new_bound(py)
                } else {
                    build_context.call1((config,))?.downcast_into()?
                }
            }
            None => PyDict::new_bound(py),
        };
        for co_name in co_names.iter()? {
            let co_name: String = co_name?.extract()?;
            let processor = PluginProcessor::new(plugin_data, &context)?;
            processors.entry(co_name).or_default().push(processor);
        }
    }
    Ok(processors)
}

pub fn load_plugins(
    py: Python,
    config: &Bound<'_, PyDict>,
) -> Result<HashMap<String, Vec<PluginProcessor>>, PyErr> {
    let kolo_plugins = PyModule::import_bound(py, "kolo.plugins")
        .expect("kolo.plugins should always be importable");
    let load = kolo_plugins
        .getattr("load_plugin_data")
        .expect("load_plugin_data should exist");
    let plugins = load
        .call1((config,))
        .expect("load_plugin_data should be callable");
    let plugins = plugins
        .downcast()
        .expect("load_plugin_data should return a list");
    load_plugin_data(py, plugins, config)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::_kolo::utils;
    use pyo3::exceptions::{PyKeyError, PyTypeError, PyValueError};
    use testresult::TestResult;

    fn assert_error_message(py: Python, err: PyErr, expected: &str) -> TestResult {
        let message = err.value_bound(py).getattr("args")?.get_item(0)?;
        let message: &str = message.extract()?;
        assert_eq!(message, expected);
        Ok(())
    }

    fn assert_keyerror(
        py: Python,
        context: &Bound<'_, PyDict>,
        plugin_data: &Bound<'_, PyDict>,
        key: &str,
    ) -> TestResult {
        let err = PluginProcessor::new(plugin_data, context).unwrap_err();
        assert!(err.is_instance_of::<PyKeyError>(py));
        assert!(err.value_bound(py).getattr("args")?.eq((key,))?);
        Ok(())
    }

    fn assert_typeerror(
        py: Python,
        context: &Bound<'_, PyDict>,
        plugin_data: &Bound<'_, PyDict>,
        message: &str,
    ) -> TestResult {
        let err = PluginProcessor::new(plugin_data, context).unwrap_err();
        assert!(err.is_instance_of::<PyTypeError>(py));
        assert_error_message(py, err, message)
    }

    #[test]
    fn test_new() -> TestResult {
        pyo3::prepare_freethreaded_python();

        Python::with_gil(|py| {
            let context = PyDict::new_bound(py);
            let plugin_data = PyDict::new_bound(py);
            assert_keyerror(py, &context, &plugin_data, "path_fragment")?;

            plugin_data.set_item("path_fragment", py.None())?;
            assert_typeerror(
                py,
                &context,
                &plugin_data,
                "'NoneType' object cannot be converted to 'PyString'",
            )?;

            plugin_data.set_item("path_fragment", "kolo").unwrap();
            assert_keyerror(py, &context, &plugin_data, "call_type")?;

            plugin_data.set_item("call_type", py.None())?;
            assert_typeerror(
                py,
                &context,
                &plugin_data,
                "'NoneType' object cannot be converted to 'PyString'",
            )?;

            plugin_data.set_item("call_type", "call").unwrap();
            assert_keyerror(py, &context, &plugin_data, "return_type")?;

            plugin_data.set_item("return_type", py.None())?;
            assert_typeerror(
                py,
                &context,
                &plugin_data,
                "'NoneType' object cannot be converted to 'PyString'",
            )?;

            plugin_data.set_item("return_type", "return")?;
            let processor = PluginProcessor::new(&plugin_data, &context)?;
            assert!(processor.context.bind(py).eq(&context)?);
            assert_eq!(processor.call_type, "call");
            assert_eq!(processor.return_type, "return");
            assert!(processor.subtype.is_none());
            assert!(processor.call.is_none());
            assert!(processor.process.is_none());
            assert!(processor
                .filename_finder
                .find("dev/kolo/middleware.py")
                .is_some());
            assert!(processor
                .filename_finder
                .find("dev/django/middleware.py")
                .is_none());

            plugin_data.set_item("subtype", py.None())?;
            assert_typeerror(
                py,
                &context,
                &plugin_data,
                "'NoneType' object cannot be converted to 'PyString'",
            )?;

            plugin_data.set_item("subtype", "subtype")?;
            let processor = PluginProcessor::new(&plugin_data, &context)?;
            assert_eq!(processor.subtype.unwrap(), "subtype");

            plugin_data.set_item("call", py.None())?;
            let processor = PluginProcessor::new(&plugin_data, &context)?;
            assert!(processor.call.is_none());

            plugin_data.set_item("process", py.None())?;
            let processor = PluginProcessor::new(&plugin_data, &context).unwrap();
            assert!(processor.process.is_none());
            Ok(())
        })
    }

    #[test]
    fn test_matches() -> TestResult {
        pyo3::prepare_freethreaded_python();

        Python::with_gil(|py| {
            let context = PyDict::new_bound(py);
            let plugin_data = PyDict::new_bound(py);
            plugin_data.set_item("path_fragment", "kolo")?;
            plugin_data.set_item("call_type", "call")?;
            plugin_data.set_item("return_type", "return")?;

            let processor = PluginProcessor::new(&plugin_data, &context)?;
            let frame = PyModule::from_code_bound(
                py,
                "
import inspect

frame = inspect.currentframe()
                ",
                "kolo/filename.py",
                "module",
            )?
            .getattr("frame")?;
            let (filename, _) = utils::filename_with_lineno(frame.downcast()?, py)?;
            let processor_match = processor.matches(py, &frame, "call", &py.None(), &filename);
            assert!(processor_match?);

            let call = PyModule::from_code_bound(
                py,
                "def call(frame, event, arg, context):
                    return event == 'call'
                ",
                "",
                "",
            )?
            .getattr("call")?;

            plugin_data.set_item("call", call)?;
            let processor = PluginProcessor::new(&plugin_data, &context)?;
            let processor_match = processor.matches(py, &frame, "call", &py.None(), &filename);
            assert!(processor_match?);
            let processor_match = processor.matches(py, &frame, "return", &py.None(), &filename);
            assert!(!processor_match?);

            let invalid_return_type = PyModule::from_code_bound(
                py,
                "def call(frame, event, arg, context):
                    return 'call'
                ",
                "",
                "",
            )?
            .getattr("call")?;

            plugin_data.set_item("call", invalid_return_type)?;
            let processor = PluginProcessor::new(&plugin_data, &context)?;
            let err = processor
                .matches(py, &frame, "call", &py.None(), &filename)
                .unwrap_err();
            assert!(err.is_instance_of::<PyTypeError>(py));
            assert_error_message(py, err, "'str' object cannot be converted to 'PyBool'")?;

            plugin_data.set_item("call", "invalid_callable")?;
            let processor = PluginProcessor::new(&plugin_data, &context)?;
            let err = processor
                .matches(py, &frame, "call", &py.None(), &filename)
                .unwrap_err();
            assert!(err.is_instance_of::<PyTypeError>(py));
            assert_error_message(py, err, "'str' object is not callable")?;
            Ok(())
        })
    }

    #[test]
    fn test_process() -> TestResult {
        pyo3::prepare_freethreaded_python();

        Python::with_gil(|py| {
            let context = PyDict::new_bound(py);
            let plugin_data = PyDict::new_bound(py);
            plugin_data.set_item("path_fragment", "kolo")?;
            plugin_data.set_item("call_type", "call")?;
            plugin_data.set_item("return_type", "return")?;

            let mut processor = PluginProcessor::new(&plugin_data, &context)?;
            let frame = PyModule::from_code_bound(
                py,
                "
import inspect

frame = inspect.currentframe()
                ",
                "kolo/filename.py",
                "module",
            )?
            .getattr("frame")?;
            let frame = frame.downcast()?;

            let data = processor.process(py, frame, "call", &py.None(), vec![])?;
            let data = data.bind(py);
            let type_ = data.get_item("type")?.unwrap();
            let type_: &str = type_.extract()?;
            assert_eq!(type_, "call");
            data.get_item("thread")?.unwrap().extract::<&str>()?;
            data.get_item("frame_id")?.unwrap().extract::<&str>()?;
            data.get_item("timestamp")?.unwrap().extract::<f64>()?;
            data.get_item("thread_native_id")?
                .unwrap()
                .extract::<u64>()?;

            let data = processor.process(py, frame, "return", &py.None(), vec![])?;
            let data = data.bind(py);
            let type_ = data.get_item("type")?.unwrap();
            let type_: &str = type_.extract()?;
            assert_eq!(type_, "return");

            let data = processor.process(py, frame, "other", &py.None(), vec![])?;
            let data = data.bind(py);
            assert!(data.get_item("type")?.is_none());

            plugin_data.set_item("subtype", "rust")?;
            let mut processor = PluginProcessor::new(&plugin_data, &context)?;
            let data = processor.process(py, frame, "return", &py.None(), vec![])?;
            let data = data.bind(py);
            let subtype = data.get_item("subtype")?.unwrap();
            let subtype: &str = subtype.extract()?;
            assert_eq!(subtype, "rust");

            let process = PyModule::from_code_bound(
                py,
                "def process(frame, event, arg, context):
                    return {
                        'event': event,
                    }
                ",
                "",
                "",
            )?
            .getattr("process")?;
            plugin_data.set_item("process", process)?;
            let mut processor = PluginProcessor::new(&plugin_data, &context)?;
            let data = processor.process(py, frame, "call", &py.None(), vec![])?;
            let data = data.bind(py);
            let event = data.get_item("event")?.unwrap();
            let event: &str = event.extract()?;
            assert_eq!(event, "call");

            let invalid_return_type = PyModule::from_code_bound(
                py,
                "def process(frame, event, arg, context):
                    return 'process'
                ",
                "",
                "",
            )?
            .getattr("process")?;
            plugin_data.set_item("process", invalid_return_type)?;
            let mut processor = PluginProcessor::new(&plugin_data, &context)?;
            let err = processor
                .process(py, frame, "call", &py.None(), vec![])
                .unwrap_err();
            assert!(err.is_instance_of::<PyTypeError>(py));
            assert_error_message(py, err, "'str' object cannot be converted to 'Mapping'")?;

            plugin_data.set_item("process", "invalid_callable")?;
            let mut processor = PluginProcessor::new(&plugin_data, &context)?;
            let err = processor
                .process(py, frame, "call", &py.None(), vec![])
                .unwrap_err();
            assert!(err.is_instance_of::<PyTypeError>(py));
            assert_error_message(py, err, "'str' object is not callable")?;

            let weird_mapping = PyModule::from_code_bound(
                py,
                "
from collections.abc import Mapping


class WeirdMapping(Mapping):
    def __getitem__(self, key):
        raise ValueError('Weird')

    def __iter__(self):
        raise ValueError('Weird')

    def __len__(self):
        raise ValueError('Weird')


def process(frame, event, arg, context):
    return WeirdMapping()
                ",
                "",
                "",
            )?
            .getattr("process")?;
            plugin_data.set_item("process", weird_mapping)?;
            let mut processor = PluginProcessor::new(&plugin_data, &context)?;
            let err = processor
                .process(py, frame, "call", &py.None(), vec![])
                .unwrap_err();
            assert!(err.is_instance_of::<PyValueError>(py));
            assert_error_message(py, err, "Weird")?;
            Ok(())
        })
    }

    #[test]
    fn test_load_plugin_data() -> TestResult {
        pyo3::prepare_freethreaded_python();

        Python::with_gil(|py| {
            let plugins = PyList::empty_bound(py);
            let config = PyDict::new_bound(py);

            let processors = load_plugin_data(py, &plugins, &config)?;
            assert_eq!(processors.len(), 0);

            let plugins = PyList::new_bound(py, vec![py.None()]);
            let err = load_plugin_data(py, &plugins, &config).unwrap_err();
            assert!(err.is_instance_of::<PyTypeError>(py));
            assert_error_message(py, err, "'NoneType' object cannot be converted to 'PyDict'")?;

            let plugin_data = PyDict::new_bound(py);
            let plugins = PyList::new_bound(py, vec![&plugin_data]);
            let err = load_plugin_data(py, &plugins, &config).unwrap_err();
            assert!(err.is_instance_of::<PyKeyError>(py));
            assert_error_message(py, err, "co_names")?;

            plugin_data.set_item("co_names", py.None())?;
            let err = load_plugin_data(py, &plugins, &config).unwrap_err();
            assert!(err.is_instance_of::<PyTypeError>(py));
            assert_error_message(py, err, "'NoneType' object is not iterable")?;

            plugin_data.set_item("co_names", (py.None(),))?;
            let err = load_plugin_data(py, &plugins, &config).unwrap_err();
            assert!(err.is_instance_of::<PyTypeError>(py));
            assert_error_message(
                py,
                err,
                "'NoneType' object cannot be converted to 'PyString'",
            )?;

            let weird_co_names = PyModule::from_code_bound(
                py,
                "
def weird_gen():
    raise ValueError('Weird')
    yield

weird = weird_gen()
                ",
                "",
                "",
            )?
            .getattr("weird")?;

            plugin_data.set_item("co_names", weird_co_names)?;
            let err = load_plugin_data(py, &plugins, &config).unwrap_err();
            assert!(err.is_instance_of::<PyValueError>(py));
            assert_error_message(py, err, "Weird")?;

            plugin_data.set_item("co_names", ("foo",))?;
            let err = load_plugin_data(py, &plugins, &config).unwrap_err();
            assert!(err.is_instance_of::<PyKeyError>(py));
            assert_error_message(py, err, "path_fragment")?;

            plugin_data.set_item("path_fragment", "kolo")?;
            plugin_data.set_item("call_type", "call_foo")?;
            plugin_data.set_item("return_type", "return_foo")?;

            let processors = load_plugin_data(py, &plugins, &config)?;
            assert_eq!(processors.len(), 1);

            plugin_data.set_item("build_context", py.None())?;
            let processors = load_plugin_data(py, &plugins, &config)?;
            assert_eq!(processors.len(), 1);

            plugin_data.set_item("build_context", "invalid callable")?;
            let err = load_plugin_data(py, &plugins, &config).unwrap_err();
            assert!(err.is_instance_of::<PyTypeError>(py));
            assert_error_message(py, err, "'str' object is not callable")?;

            let invalid_return_type = PyModule::from_code_bound(
                py,
                "def build_context(config):
                    return 'invalid'
                ",
                "",
                "",
            )?
            .getattr("build_context")?;
            plugin_data.set_item("build_context", invalid_return_type)?;
            let err = load_plugin_data(py, &plugins, &config).unwrap_err();
            assert!(err.is_instance_of::<PyTypeError>(py));
            assert_error_message(py, err, "'str' object cannot be converted to 'PyDict'")?;

            let build_context = PyModule::from_code_bound(
                py,
                "def build_context(config):
                    return {'frame_ids': []}
                ",
                "",
                "",
            )?
            .getattr("build_context")?;
            plugin_data.set_item("build_context", build_context)?;
            let processors = load_plugin_data(py, &plugins, &config)?;
            assert_eq!(processors.len(), 1);
            assert_eq!(processors["foo"].len(), 1);
            assert!(processors["foo"][0]
                .context
                .bind(py)
                .get_item("frame_ids")?
                .unwrap()
                .is_instance_of::<PyList>());
            Ok(())
        })
    }

    #[test]
    fn test_load_plugins() -> TestResult {
        pyo3::prepare_freethreaded_python();

        Python::with_gil(|py| {
            let config = PyDict::new_bound(py);
            let processors = load_plugins(py, &config)?;
            assert!(!processors.is_empty());
            Ok(())
        })
    }
}
