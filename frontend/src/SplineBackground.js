import React from "react";
import Spline from "@splinetool/react-spline";

export default function SplineBackground({ scene }) {
  return (
    <div className="spline-bg">
      <Spline scene={scene} renderOnDemand={true} />
    </div>
  );
}