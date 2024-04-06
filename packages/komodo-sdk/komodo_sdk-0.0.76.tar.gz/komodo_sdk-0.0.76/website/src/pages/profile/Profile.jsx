import React, { useContext, useRef, useState } from "react";
import Sidebar from "../../components/Sidebar";
import userProfile from "../../assets/userProfile.svg";
import trash from "../../assets/trash.svg";
import gallery from "../../assets/gallery.svg";
import { FiTrash2 } from "react-icons/fi";
import { TbPhoto } from "react-icons/tb";
import CustomInput from "../../components/inputs/CustomInputs";
import { useNavigate } from "react-router-dom";
import person from "../../../src/images/person.png";
import roleContext from "../../contexts/roleContext";

const Profile = () => {
  const navigate = useNavigate();
  const handleChange = () => { };

  const [logoImage, setLogoImage] = useState(null);
  const fileInputRef = useRef(null);
  const agentContext = useContext(roleContext);
  console.log('agentContext :>> ', agentContext?.agentList?.type);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onloadend = () => {
      setLogoImage(reader.result);
    };
    if (file) {
      reader.readAsDataURL(file);
    }
  };

  const handleChooseFile = () => {
    fileInputRef.current.click();
  };

  const handleLogOut = () => {
    localStorage.removeItem("komodoUser");
    {
      agentContext?.agentList?.type === "retail" ? (
        navigate("/home")
      ) : (
        navigate("/login")
      )
    }
    window.location.reload();
  };

  return (
    <div className="flex">
      <div className="w-[77px] xl:w-[60px]">
        <Sidebar />
      </div>

      <div className="flex-1 flex flex-col h-[100vh] overflow-auto  ">
        <div className="h-100 border-b border-customGray  w-[100%] px-8 py-4 flex flex-col justify-between gap-3">
          <h2 className="text-[26px] font-cerebri text-blackText leading-[27px]">My Profile</h2>

          <h6 className="text-[18px] font-cerebriregular text-blackText">Profile</h6>
        </div>
        <div className="px-8 py-4 flex-1">
          <div className=" font-cerebriregular mt-4 mb-6">
            <div className="flex gap-8">
              <img src={logoImage || person} alt="" className="w-[126px] h-[126px] rounded-xl" />
              <div className="text-customColor text-[16px] gap-4 justify-center flex flex-col">
                <div
                  className="bg-customBg cursor-pointer p-3 flex w-[114px] rounded-[10px] gap-3"
                  onClick={handleChooseFile}
                >
                  {/* <img src={gallery} alt="" /> */}
                  <TbPhoto className="text-[22px] rounded-3xl" />
                  <span className="">Change</span>
                </div>
                <div className="p-3 flex w-[114px] rounded-[10px] gap-3 border border-customBorderDark">
                  {/* <img src={trash} alt="" /> */}
                  <FiTrash2 className="text-[22px]" />
                  <span>Remove</span>
                </div>
              </div>

              <input
                type="file"
                accept="image/*"
                ref={fileInputRef}
                style={{ display: "none" }}
                onChange={handleFileChange}
              />
            </div>
            {/* Content for the second row in the second column */}
          </div>
          <div className="w-1/2 lg:w-[100%]">
            <div className="grid grid-cols-2 md:grid-cols-1 gap-3 ">
              <CustomInput label="First Name" placeholder="First Name" onChange={handleChange} value="" />
              <CustomInput label="Last Name" placeholder="Last Name" onChange={handleChange} value="" />
              <CustomInput label="Email" placeholder="First Name" onChange={handleChange} value="" />
              <CustomInput
                label="Phone Number"
                placeholder="Phone Number"
                onChange={handleChange}
                value="ms"
              />
              {/* <div className="font-cerebriregular" >
              <label for="inputField1" className="block mb-2 text-[18px]">
                First Name
              </label>
              <input
                id="First Name"
                type="text"
                className="border rounded-[10px] px-4 py-3 w-full bg-lightSky
                border-borderSky text-[16px] "
                placeholder="First Name"
              />
            </div> */}
              {/* <div >
              <label for="inputField2" className="block mb-2">
                Input Field 2
              </label>
              <input
                id="inputField2"
                type="text"
                className="border rounded px-4 py-2 w-full"
              />
            </div> */}
            </div>
            <div className="grid grid-cols-1 gap-4 w-1/2 md:w-[100%]">
              <div className="mt-4 flex flex-col gap-[4px]">
                <p>Change Password</p>
                <p className="text-[14px] text-greyText">Here you can set your new password</p>
              </div>

              <CustomInput label="Old Password" placeholder="Old Password" onChange={handleChange} value="" />
              <CustomInput label="New Password" placeholder="New Password" onChange={handleChange} value="" />
              <CustomInput
                label="Confirm Password"
                placeholder="Confirm Password"
                onChange={handleChange}
                value=""
              />
              <button
                className="bg-customBgDark py-4 px-5 text-white w-[152px] rounded-[10px]"
                onClick={handleLogOut}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
