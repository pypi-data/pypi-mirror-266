import React, { useContext } from "react";
import Sidebar from "../components/Sidebar";
import { useFormik } from "formik";
import * as Yup from "yup";
import { Link, useLocation, useNavigate } from "react-router-dom";
import roleContext from "../contexts/roleContext";
import { ApiGet } from "../API/API_data";
import { ErrorToast, SuccessToast } from "../helpers/Toast";
import { API_Path } from "../API/ApiComment";
import bg from "../images/login.png";

const Signup = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const context = useContext(roleContext);

  const validationSchema = Yup.object().shape({
    email: Yup.string().email("Invalid email").required("Email is required"),
    password: Yup.string().required("Password is required"),
    cpassword: Yup.string().required("Confirm Password is required"),
  });

  const formik = useFormik({
    initialValues: {
      email: "",
      password: "",
      cpassword: "",
    },
    validationSchema: validationSchema,
    onSubmit: async (values) => {
      try {
        const checkLogin = await ApiGet(API_Path.userSignUpUrl, values.email);
        if (checkLogin?.status === 200) {
          localStorage.setItem("komodoUser", JSON.stringify(checkLogin.data));
          context?.setUser(checkLogin.data.email);
          SuccessToast("Login successful");
          navigate("/chat");
        }
      } catch (error) {
        console.log("user details get ::error", error);
        ErrorToast(error?.data?.detail || "Something went wrong");
      }
    },
  });

  return (
    <>
      <div className="grid grid-rows-1">
        <div className="grid grid-cols-12">
          {/* <div className="col-span-1">
            <Sidebar />
          </div> */}

          <div className="col-span-6 md:hidden">
            <h1 className="text-3xl font-cerebrisemibold absolute top-10 left-10">
              {context?.company}
            </h1>
            <img src={bg} alt="bg" className="w-full h-screen p-3" />
          </div>

          <div className="col-span-6 md:col-span-12 w-full flex flex-col justify-center items-center h-[calc(100vh-57px)]">
            <form
              onSubmit={formik.handleSubmit}
              className="w-[60%] lg:w-[70%] xs:w-[95%]"
            >
              <div className="">
                <div className="text-[25px] text-[#0C1421] font-cerebriregular">
                  Create Account 👋
                </div>

                <div className="font-cerebriregular text-[16px] text-[#313957] mt-2 mb-10">
                  Enter your email and password to create account
                </div>
              </div>

              <div>
                <h1 className="text-[#495057] sm:text-[17px] text-[18px] font-cerebri leading-[30px]">
                  Email
                </h1>
                <input
                  type="text"
                  placeholder="Enter Email"
                  name="email"
                  value={formik.values.email}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  className="text-[#495057] bg-[#F2F6FF] text-[16px] font-cerebriregular leading-[20.32px] border border-[#DDE8FF] rounded-md w-full px-3 py-3.5 outline-none mt-1"
                />
                {formik.touched.email && formik.errors.email && (
                  <p className="text-red-500 mt-2">{formik.errors.email}</p>
                )}
              </div>

              <div className="mt-5">
                <h1 className="text-[#495057] sm:text-[17px] text-[18px] font-cerebri leading-[30px]">
                  Password
                </h1>
                <input
                  type="password"
                  placeholder="Enter Password"
                  name="password"
                  value={formik.values.password}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  className="text-[#495057] bg-[#F2F6FF] text-[16px] font-cerebriregular leading-[20.32px] border border-[#DDE8FF] rounded-md w-full px-3 py-3.5 outline-none mt-1"
                />
                {formik.touched.password && formik.errors.password && (
                  <p className="text-red-500 mt-2">{formik.errors.password}</p>
                )}
              </div>

              <div className="mt-5">
                <h1 className="text-[#495057] sm:text-[17px] text-[18px] font-cerebri leading-[30px]">
                  Confirm Password
                </h1>
                <input
                  type="password"
                  placeholder="Enter Password"
                  name="cpassword"
                  value={formik.values.cpassword}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  className="text-[#495057] bg-[#F2F6FF] text-[16px] font-cerebriregular leading-[20.32px] border border-[#DDE8FF] rounded-md w-full px-3 py-3.5 outline-none mt-1"
                />
                {formik.touched.password && formik.errors.cpassword && (
                  <p className="text-red-500 mt-2">{formik.errors.cpassword}</p>
                )}
              </div>

              <div className="font-cerebriregular text-[#316FF6] text-[16px] mt-3.5 text-right">
                Forgot Password?
              </div>

              <button
                type="submit"
                className="text-[#fff] text-[19px] font-cerebri leading-[24.13px] text-center bg-[#316FF6] lg:px-3 w-full py-3.5 rounded-md mt-3.5"
              >
                Sign up
              </button>

              <div class="flex items-center mt-9 gap-3">
                <div class="flex-1 h-[1px] bg-[#CFDFE2]"></div>
                <div className="text-[#294957] text-[15px] font-cerebriregular mt-1">
                  Or
                </div>
                <div class="flex-1 h-[1px] bg-[#CFDFE2]"></div>
              </div>

              <div className="font-cerebriregular flex items-center justify-center gap-2 mt-7 text-[17px]">
                Already have an account?{" "}
                <Link to="/login" className="text-[#316FF6] font-cerebri">
                  Sign In
                </Link>
              </div>

              <div className="flex items-center justify-center">
                <Link
                  to="/terms"
                  className="text-[#959CB6] text-[16px] absolute bottom-4"
                >
                  Terms and Conditions
                </Link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default Signup;
