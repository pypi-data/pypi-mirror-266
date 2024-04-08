use hex_renderer::pattern_utils::Angle;

use pyo3::{pymodule, Python, types::PyModule, PyResult};

pub mod classes;
#[pymodule]
fn hex_renderer_py(py: Python, m: &PyModule) -> PyResult<()> {
    
    classes::color::add_class(py, m)?;
    classes::marker::add_class(py, m)?;
    classes::point::add_class(py, m)?;
    classes::end_point::add_class(py, m)?;
    classes::intersections::add_class(py, m)?;
    classes::triangle::add_class(py, m)?;
    classes::overload_options::add_class(py, m)?;
    classes::collision_option::add_class(py, m)?;
    classes::lines::add_class(py, m)?;


    m.add_class::<classes::angle_sig::AngleSig>()?;

    classes::grid_pattern_options::add_class(py, m)?;
    classes::grid_options::add_class(py, m)?;

    m.add_class::<classes::pattern_variant::PyPatternVariant>()?;

    
    classes::grids::initialize_classes(m)?;
    

    Ok(())
}


#[allow(clippy::ptr_arg)]
fn angles_to_string(inp: &Vec<Angle>) -> String {
    inp.iter()
        .map(|angle| match angle {
            Angle::Forward => 'w',
            Angle::Right => 'e',
            Angle::BackRight => 'd',
            Angle::Back => 's',
            Angle::BackLeft => 'a',
            Angle::Left => 'q',
        })
        .collect()
}

#[cfg(test)]
pub mod tests {
    use std::{fs::{File, self}, io::Write};

    const INIT_PY: &str = "
from .hex_renderer_py import *

__doc__ = hex_renderer_py.__doc__
if hasattr(hex_renderer_py, \"__all__\"):
    __all__ = hex_renderer_py.__all__

";

    #[test]
    fn print_stuffs() -> std::io::Result<()> {
        let (types, declarations, docs) = ::interface_macros::collect_stored_types();
        let mut file = File::create("hex_renderer_py/__init__.pyi")?;
        file.write_all(types.as_bytes())?;

        let mut init_file = File::create("hex_renderer_py/__init__.py")?;
        init_file.write_all(INIT_PY.as_bytes())?;
        init_file.write_all(declarations.as_bytes())?;

        //let mut docs_file = File::create("test/autodoc.rst")?;
        //docs_file.write_all(docs.as_bytes())?;
        fn create_module(module: interface_macros::DocModule, name: String, path: String) -> std::io::Result<()> {
            fs::create_dir_all(&path)?;
            let mut file = File::create(path.clone() + "/index.rst")?;
            
            file.write_all(format!("{name}\n").as_bytes())?;
            file.write_all("===============================================\n\n".as_bytes())?;

            const TAB: &str = "  ";
            file.write_all(".. toctree::\n".as_bytes())?;
            file.write_all(format!("{TAB}:maxdepth: 1\n").as_bytes())?;
            file.write_all(format!("{TAB}:caption: Sub Modules:\n\n").as_bytes())?;

            for module_name in module.sub_modules.keys() {
                file.write_all(format!("{TAB}{module_name}/index\n").as_bytes())?;
            }
            file.write_all("\n".as_bytes())?;

            file.write_all(module.inner.join("\n").as_bytes())?;

            for (name, sub_module) in module.sub_modules {
                create_module(sub_module, name.clone(), path.clone() + "/" + &name)?;
            }
            Ok(())
        }
        create_module(docs, "API Documentation".to_string(), "docs/autodoc/".to_string())?;
        Ok(())
    }
}