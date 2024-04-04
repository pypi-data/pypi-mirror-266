use bstr::Finder;
use once_cell::sync::Lazy;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyFrame;

macro_rules! count {
        // Macro magic to find the length of $path
        // https://youtu.be/q6paRBbLgNw?t=4380
        ($($element:expr),*) => {
            [$(count![@SUBSTR; $element]),*].len()
        };
        (@SUBSTR; $_element:expr) => {()};
    }

macro_rules! finder {
        ($name:ident = $path:expr) => {
            static $name: Lazy<Finder> = Lazy::new(|| Finder::new($path));
        };
        (pub $name:ident = $path:expr) => {
            pub static $name: Lazy<Finder> = Lazy::new(|| Finder::new($path));
        };
        (pub $name:ident = $($path:expr),+ $(,)?) => {
            pub static $name: Lazy<[Finder; count!($($path),*)]> = Lazy::new(|| {
                [
                    $(Finder::new($path),)+
                ]
            });
        };

    }

finder!(FROZEN_FINDER = "<frozen ");
finder!(EXEC_FINDER = "<string>");

#[cfg(target_os = "windows")]
mod windows {
    use bstr::Finder;
    use once_cell::sync::Lazy;
    finder!(pub LIBRARY_FINDERS = "lib\\python", "\\site-packages\\", "\\x64\\lib\\");
    finder!(pub LOWER_PYTHON_FINDER = "\\python\\");
    finder!(pub UPPER_PYTHON_FINDER = "\\Python\\");
    finder!(pub LOWER_LIB_FINDER = "\\lib\\");
    finder!(pub UPPER_LIB_FINDER = "\\Lib\\");
    finder!(pub KOLO_FINDERS = "\\kolo\\config.py",
        "\\kolo\\db.py",
        "\\kolo\\django_schema.py",
        "\\kolo\\filters\\",
        "\\kolo\\generate_tests\\",
        "\\kolo\\git.py",
        "\\kolo\\__init__.py",
        "\\kolo\\__main__.py",
        "\\kolo\\middleware.py",
        "\\kolo\\profiler.py",
        "\\kolo\\pytest_plugin.py",
        "\\kolo\\serialize.py",
        "\\kolo\\utils.py",
        "\\kolo\\version.py");
}
#[cfg(target_os = "windows")]
use windows::*;

#[cfg(not(target_os = "windows"))]
mod not_windows {
    use bstr::Finder;
    use once_cell::sync::Lazy;
    finder!(pub LIBRARY_FINDERS = "lib/python", "/site-packages/");
    finder!(pub KOLO_FINDERS = "/kolo/config.py",
        "/kolo/db.py",
        "/kolo/django_schema.py",
        "/kolo/filters/",
        "/kolo/generate_tests/",
        "/kolo/git.py",
        "/kolo/__init__.py",
        "/kolo/__main__.py",
        "/kolo/middleware.py",
        "/kolo/profiler.py",
        "/kolo/pytest_plugin.py",
        "/kolo/serialize.py",
        "/kolo/utils.py",
        "/kolo/version.py");
}
#[cfg(not(target_os = "windows"))]
use not_windows::*;

pub fn library_filter(co_filename: &str) -> bool {
    for finder in LIBRARY_FINDERS.iter() {
        if finder.find(co_filename).is_some() {
            return true;
        }
    }
    #[cfg(target_os = "windows")]
    {
        (LOWER_PYTHON_FINDER.find(co_filename).is_some()
            || UPPER_PYTHON_FINDER.find(co_filename).is_some())
            && (LOWER_LIB_FINDER.find(co_filename).is_some()
                || UPPER_LIB_FINDER.find(co_filename).is_some())
    }
    #[cfg(not(target_os = "windows"))]
    false
}

pub fn frozen_filter(co_filename: &str) -> bool {
    FROZEN_FINDER.find(co_filename).is_some()
}

pub fn exec_filter(co_filename: &str) -> bool {
    EXEC_FINDER.find(co_filename).is_some()
}

pub fn kolo_filter(co_filename: &str) -> bool {
    KOLO_FINDERS
        .iter()
        .any(|finder| finder.find(co_filename).is_some())
}

pub fn attrs_filter(
    co_filename: &str,
    pyframe: &Bound<'_, PyFrame>,
    py: Python,
) -> Result<bool, PyErr> {
    if co_filename.starts_with("<attrs generated") {
        return Ok(true);
    }

    let previous = pyframe.getattr(intern!(py, "f_back"))?;
    if previous.is_none() {
        return Ok(false);
    }

    let f_code = previous.getattr(intern!(py, "f_code"))?;
    let co_filename = f_code.getattr(intern!(py, "co_filename"))?;
    let co_filename = co_filename.extract::<String>()?;

    #[cfg(target_os = "windows")]
    let make_path = "attr\\_make.py";
    #[cfg(not(target_os = "windows"))]
    let make_path = "attr/_make.py";

    if co_filename.is_empty() {
        let previous = previous.getattr(intern!(py, "f_back"))?;
        if previous.is_none() {
            return Ok(false);
        }
        let f_code = previous.getattr(intern!(py, "f_code"))?;
        let co_filename = f_code.getattr(intern!(py, "co_filename"))?;
        let co_filename = co_filename.extract::<String>()?;
        Ok(co_filename.ends_with(make_path))
    } else {
        Ok(co_filename.ends_with(make_path))
    }
}

pub fn pytest_generated_filter(
    co_filename: &str,
    _pyframe: &Bound<'_, PyFrame>,
    _py: Python,
) -> bool {
    co_filename == "<pytest match expression>"
}
