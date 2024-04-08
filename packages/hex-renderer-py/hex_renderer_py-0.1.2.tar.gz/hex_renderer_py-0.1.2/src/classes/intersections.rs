use hex_renderer::options::{Point, Intersections, EndPoint};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::{point::PyPoint, end_point::PyEndPoint};

pub fn add_class(py: Python, m: &PyModule) -> PyResult<()> {
    let sub_m = PyModule::new(py, "Intersections")?;
    sub_m.add_class::<PyIntersectionsNothing>()?;
    sub_m.add_class::<PyIntersectionsUniformPoints>()?;
    sub_m.add_class::<PyIntersectionsEndsAndMiddle>()?;
    
    m.add_submodule(sub_m)?;

    Ok(())
}

#[py_gen(bridge = Intersections)]
#[derive(Clone)]
///How to draw all the points in a pattern, including start, end, and middle points
pub enum PyIntersections {
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Doesn't draw any points
    Nothing,
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draws the same point for everything, including start and end
    UniformPoints(
        #[py_gen(name = "point", bridge = PyPoint)]
        Point,
    ),
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draws a different point for the start, end, and middle
    EndsAndMiddle {
        #[py_gen(bridge = PyEndPoint)]
        start: EndPoint,
        #[py_gen(bridge = PyPoint)]
        middle: Point,
        #[py_gen(bridge = PyEndPoint)]
        end: EndPoint
    }
}