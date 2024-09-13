import Autodesk.Revit.DB

def get_framing_endpoints(framing_elem):
  framing_curve = framing_elem.Location.Curve
  endpt1 = framing_curve.GetEndPoint(0)
  endpt2 = framing_curve.GetEndPoint(1)
  framing_endpts = [endpt1, endpt2]
  return framing_endpts