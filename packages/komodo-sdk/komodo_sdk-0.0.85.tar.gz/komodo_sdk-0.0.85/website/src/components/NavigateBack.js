import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const NavigateBack = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const detailsId = location?.pathname.split("/details/")[1];
  // const chatdocId = location?.pathname.split("/chatdoc/")[1];

  useEffect(() => {
    const paths = [
      "",
      "/",
      "/terms",
      "/chat",
      "/chatdoc",
      `/details/${detailsId}`,
      "/chatdoc/:id",
      "/document",
      "/profile",
      "/settings",
      "/privacy",
    ];
    if (!paths?.includes(location?.pathname)) {
      navigate(-1);
    }
  }, []);

  return <div></div>;
};

export default NavigateBack;

// import React, { useEffect } from "react";
// import { useNavigate } from "react-router-dom";

// const NavigateBack = () => {
//   const navigate = useNavigate();
//   // useEffect(() => {
//   //   navigate(-1);
//   //   // window.history.forward();
//   // }, []);

//   const handleClick = () => {
//     navigate(-1);
//   };

//   return (
//     <div className="cursor-pointer" onClick={handleClick}>
//       Back{" "}
//     </div>
//   );
// };

// export default NavigateBack;
