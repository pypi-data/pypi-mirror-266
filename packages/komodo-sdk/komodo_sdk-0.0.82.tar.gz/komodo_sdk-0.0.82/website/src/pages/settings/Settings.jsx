import React, { useContext, useEffect, useRef, useState } from "react";
import Sidebar from "../../components/Sidebar";
import apperance from "../../assets/magicpen.svg";
import setting from "../../assets/setting.svg";
import apperance1 from "../../assets/magicpen-1.svg";
import setting1 from "../../assets/setting-1.svg";
import botAvatar from "../../assets/botAvatar.svg";
import person from "../../../src/images/person.png";
import square from "../../assets/square.svg";
import message from "../../assets/message.svg";
import headphone from "../../assets/headphone.svg";
import gray from "../../assets/gray.svg";
import yellow from "../../assets/yellow.svg";
import multi from "../../assets/multi.png";
import indigo from "../../assets/indigo.svg";
import aubergine from "../../assets/aubergine.png";
import jade from "../../assets/jade.svg";
import clementine from "../../assets/clementine.svg";
import barbra from "../../assets/barbra.svg";
import lagoon from "../../assets/lagoon.svg";
import ColorPicker from "react-pick-color";
import { TbSettings2 } from "react-icons/tb";
import { PiMagicWand } from "react-icons/pi";
import CustomInput from "../../components/inputs/CustomInputs";
import { Link } from "react-router-dom";
import { Box, Modal } from "@mui/material";
import { API_Path } from "../../API/ApiComment";
import { ApiGet } from "../../API/API_data";
import { SuccessToast } from "../../helpers/Toast";
import Select from "react-select";

const style = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "fit-content",
  bgcolor: "background.paper",
  border: "none",
  boxShadow: 20,
  p: 4,
  borderRadius: "25px",
  outline: "none",
};

const Settings = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [logoImage, setLogoImage] = useState(null);
  const [color, setColor] = useState("#fff");
  const [open, setOpen] = useState(false);
  const [isChecked1, setIsChecked1] = useState(false);
  const [isChecked, setIsChecked] = useState(false);
  const fileInputRef = useRef(null);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleTabClick = (index) => {
    setSelectedTab(index);
  };

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

  const handleChange = () => { };

  const handleColorClick = (colorName) => {
    const hexToRgb = (hex) => {
      return {
        r: parseInt(hex.substring(1, 3), 16),
        g: parseInt(hex.substring(3, 5), 16),
        b: parseInt(hex.substring(5, 7), 16),
      };
    };

    const darkenColor = (color, percentage) => {
      return Math.round(color * (1 - percentage));
    };

    const darkenPercentage = 0.8;

    const rgbColor = hexToRgb(colorName);

    const darkR = darkenColor(rgbColor.r, darkenPercentage);
    const darkG = darkenColor(rgbColor.g, darkenPercentage);
    const darkB = darkenColor(rgbColor.b, darkenPercentage);

    const darkColor = `#${darkR.toString(16).padStart(2, "0")}${darkG.toString(16).padStart(2, "0")}${darkB
      .toString(16)
      .padStart(2, "0")}`;

    const opacityDecimal = 0.1;
    const opacityHex = Math.round(opacityDecimal * 255).toString(16);

    const secondaryColor = `${colorName}${opacityHex}`;

    var r = document.querySelector(":root");
    r.style.setProperty("--primary-color", colorName);
    r.style.setProperty("--secondary-color", secondaryColor);
    r.style.setProperty("--dark-color", darkColor);

    let data = JSON.parse(localStorage.getItem("komodoUser"));
    localStorage.setItem(
      "komodoUser",
      JSON.stringify({ ...data, color: colorName, bgcolor: secondaryColor, bgdark: darkColor })
    );

    handleClose();
  };

  const handleCheckboxChange = (e) => {
    const checked = e.target.checked;
    setIsChecked(checked);
  };

  const handleCheckboxChange1 = (e) => {
    const checked = e.target.checked;
    setIsChecked1(checked);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await ApiGet(API_Path.applianceIndexUrl);
        if (res?.status === 200) {
          SuccessToast("Index all data sources for the appliance.");
        }
      } catch (error) {
        console.error("Error fetching API:", error);
      }
    };
    if (isChecked) {
      fetchData();
    }
  }, [isChecked]);

  useEffect(() => {
    const fetchData1 = async () => {
      try {
        const res = await ApiGet(API_Path.applianceReindexUrl);
        if (res?.status === 200) {
          SuccessToast("ReIndex all data sources for the appliance.");
        }
      } catch (error) {
        console.error("Error fetching API:", error);
      }
    };
    if (isChecked1) {
      fetchData1();
    }
  }, [isChecked1]);

  const options = [
    { value: "English", label: "English" },
    { value: "Spanish", label: "Spanish" },
    { value: "French", label: "French" }
  ];

  const style = {
    control: (base) => ({
      ...base,
      cursor: "pointer",
      border: "0",
      backgroundColor: '#f3f4f6',
      lineHeight: '24px',
      fontSize: "16px",
      borderRadius: '9px',
      boxShadow: 'none'
    }),
    option: (base, { isSelected }) => ({
      ...base,
      backgroundColor: isSelected ? "var(--primary-color)" : "#ffffff",
      cursor: "pointer",
      color: isSelected ? "#fff" : "#000",
      " &:hover": {
        backgroundColor: "var(--secondary-color)",
        color: "#000",
      },
    }),
    // placeholder: (defaultStyles) => {
    //   return {
    //     ...defaultStyles,
    //     fontSize: "5px",
    //   };
    // },
  };

  return (
    <>
      <div className="flex font-cerebriregular">
        <div>
          <Sidebar />
        </div>

        <div className="flex-1 flex-col h-[100vh] overflow-auto">
          <div className="h-100 border-b border-customGray  w-[100%] px-8 xs:px-2 py-4 flex flex-col justify-between gap-3">
            <h2 className="text-[26px] font-cerebri text-blackText leading-[27px]">Settings</h2>

            <h6 className="text-[18px] font-cerebri text-blackText">Settings</h6>
          </div>
          <div className="px-6 xs:px-2 py-10 flex-1">
            <div className="grid grid-cols-1 gap-9">
              <div className="flex bg-customBg rounded-[10px] p-2 xs:p-1 w-[335px] xs:w-[290px] sm:w-[310px] h-[58px]">
                <div
                  className={`px-5 xs:px-2 xs:py-0 py-2 sm:px-3 sm:text-[16px] flex gap-2 justify-center items-center cursor-pointer rounded-[10px] ${selectedTab === 0 ? "bg-white text-customColor" : "bg-transparent"
                    }`}
                  onClick={() => handleTabClick(0)}
                >
                  {/* <img src={selectedTab === 0 ? apperance : apperance1} className="w-5 h-5" alt="" /> */}
                  <PiMagicWand className="text-[22px]" />
                  <span>Appearance</span>
                </div>
                <div
                  className={`px-4 xs:px-2 xs:py-0 py-2 sm:px-3 sm:text-[16px] flex gap-2 justify-center items-center cursor-pointer rounded-[10px] ${selectedTab === 1 ? "bg-white text-customColor" : "bg-transparent"
                    }`}
                  onClick={() => handleTabClick(1)}
                >
                  {/* <img src={selectedTab === 0 ? setting : setting1} className="w-5 h-5" alt="" /> */}
                  <TbSettings2 className="text-[20px]" />
                  <span className="mt-0.5">Other Setting</span>
                </div>
              </div>

              {selectedTab === 0 && (
                <div className="grid grid-cols-1 gap-9">
                  <div className="w-1/4 md:w-[100%]">
                    <CustomInput
                      label="Bot Name *"
                      placeholder="Bot Name"
                      onChange={handleChange}
                      className="bg-customBg"
                      value=""
                    />
                  </div>
                  <div>
                    <p className="text-[18px] mb-3">Bot Avatar </p>
                    <div className="flex gap-4">
                      <img src={logoImage || person} alt="" className="w-[62px] h-[62px] rounded-xl" />
                      <div className="text-[16px] flex flex-col justify-around">
                        <p className="text-customColor underline cursor-pointer" onClick={handleChooseFile}>
                          Change Logo
                        </p>
                        <p className="text-greyText">JPG/PNG up to 5 MB</p>
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
                  {/* <div>
                  <p className="text-[18px] mb-3">Select button icon </p>
                  <div className="flex gap-4">
                    <img src={botAvatar} />
                    <div className="rounded-[10px] border border-customGray w-[72px] flex items-center justify-center">
                      <img src={message} />
                    </div>
                    <div className="rounded-[10px] border border-customGray w-[72px] flex items-center justify-center">
                      <img src={headphone} />
                    </div>
                    <div className="rounded-[10px] border border-customGray w-[72px] flex items-center justify-center">
                      <img src={square} />
                    </div>
                  </div>
                </div> */}

                  <div>
                    <p className="text-[18px] mb-3">Themes</p>
                    <div className="flex items-center gap-6">
                      <div>
                        <div className="flex flex-row gap-3 sm:grid sm:grid-cols-4">
                          <div
                            className="rounded-[10px] border border-customGray gap-3 px-3.5 w-[178px] py-3.5 flex items-center cursor-pointer"
                            onClick={() => handleColorClick("#C5C5C5")}
                          >
                            <img src={gray} alt="gray" />
                            <div className="text-[16px] font-cerebriregular text-[#797C8C]">Gray</div>
                          </div>

                          <div
                            className="rounded-[10px] border border-customGray gap-3 px-3.5 w-[178px] py-3.5 flex items-center cursor-pointer"
                            onClick={() => handleColorClick("#ffdd53")}
                          >
                            <img src={yellow} alt="yellow" />
                            <div className="text-[16px] font-cerebriregular text-[#797C8C]">Banana</div>
                          </div>

                          <div
                            className="rounded-[10px] border border-customGray gap-3 px-3.5 w-[178px] py-3.5 flex items-center cursor-pointer"
                            onClick={() => handleColorClick("#102171")}
                          >
                            <img src={indigo} alt="indigo" />
                            <div className="text-[16px] font-cerebriregular text-[#797C8C]">Mood Indigo</div>
                          </div>

                          <div
                            className="rounded-[10px] border border-customGray gap-3 px-3.5 w-[178px] py-3.5 flex items-center cursor-pointer"
                            onClick={() => handleColorClick("#472C4C")}
                          >
                            <img src={aubergine} alt="aubergine" />
                            <div className="text-[16px] font-cerebriregular text-[#797C8C]">Aubergine</div>
                          </div>
                        </div>

                        <div className="flex gap-3 sm:grid sm:grid-cols-4 mt-3">
                          <div
                            className="rounded-[10px] border border-customGray gap-3 px-3.5 w-[178px] py-3.5 flex items-center cursor-pointer"
                            onClick={() => handleColorClick("#00A86B")}
                          >
                            <img src={jade} alt="jade" />
                            <div className="text-[16px] font-cerebriregular text-[#797C8C]">Jade</div>
                          </div>

                          <div
                            className="rounded-[10px] border border-customGray gap-3 px-3.5 w-[178px] py-3.5 flex items-center cursor-pointer"
                            onClick={() => handleColorClick("#E96E00")}
                          >
                            <img src={clementine} alt="clementine" />
                            <div className="text-[16px] font-cerebriregular text-[#797C8C]">Clementine</div>
                          </div>

                          <div
                            className="rounded-[10px] border border-customGray gap-3 px-3.5 w-[178px] py-3.5 flex items-center cursor-pointer"
                            onClick={() => handleColorClick("#FF8CB1")}
                          >
                            <img src={barbra} alt="barbra" />
                            <div className="text-[16px] font-cerebriregular text-[#797C8C]">Barbra</div>
                          </div>

                          <div
                            className="rounded-[10px] border border-customGray gap-3 px-3.5 w-[178px] py-3.5 flex items-center cursor-pointer"
                            onClick={() => handleColorClick("#046999")}
                          >
                            <img src={lagoon} alt="lagoon" />
                            <div className="text-[16px] font-cerebriregular text-[#797C8C]">Lagoon</div>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col items-center cursor-pointer" onClick={handleOpen}>
                        <div className="rounded-[10px] border border-customGray gap-3 px-5 py-5 flex">
                          <img src={multi} alt="multi" />
                        </div>

                        <div className="font-cerebriregular text-[18px] text-[#797C8C] mt-4">
                          Custom Themes
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <Modal
                open={open}
                onClose={handleClose}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
              >
                <Box sx={style}>
                  <ColorPicker color={color} onChange={(color) => setColor(color.hex)} />

                  <div className="flex items-center justify-center mt-4 gap-3">
                    <div
                      className="text-[18px] font-cerebriregular text-[#3C3C3C] border border-customBorder rounded-lg py-2 px-5 shadow-drop cursor-pointer"
                      onClick={handleClose}
                    >
                      Cancel
                    </div>

                    <div
                      className="text-[18px] font-cerebriregular text-[#FFFFFF] bg-customBgDark rounded-lg py-2 px-7 cursor-pointer"
                      onClick={() => handleColorClick(color)}
                    >
                      Save
                    </div>
                  </div>
                </Box>
              </Modal>

              {selectedTab === 1 && (
                <div className="grid grid-cols-1 gap-10 w-1/3 lg:w-[100%] font-cerebriregular text-[16px]">
                  {/* <div>
                    <label htmlFor="language" className="block mb-2">
                      Language
                    </label>
                    <select
                      id="language"
                      className="w-[310px] xs:w-[100%] h-12 p-2 border border-gray-300 rounded-[10px] shadow-sm bg-gray-100 focus:outline-none"
                    // value={selectedLanguage}
                    // onChange={handleLanguageChange}
                    >
                      <option value="English">English</option>
                      <option value="Spanish">Spanish</option>
                      <option value="French">French</option>
                    </select>
                  </div> */}

                  <div>
                    <label htmlFor="language" className="block mb-2">
                      Language
                    </label>
                    <Select
                      id="language"
                      options={options}
                      styles={style}
                      defaultValue={options.find(option => option.value === "English")}
                      className="w-[310px] xs:w-[100%] settingbox"
                    />
                  </div>

                  <div className="flex justify-between">
                    <p>Always show code when using data analyst</p>
                    {/* <label className="inline-flex items-center cursor-pointer">
                      <input type="checkbox" value="" className="sr-only peer" />
                      <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                    </label> */}
                    <label className="inline-flex items-center cursor-pointer">
                      <input type="checkbox" value="" className="sr-only peer" />
                      <div className="relative w-12 h-7 bg-customBg peer-focus:outline-none rounded-full peer dark:bg-customBg peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white peer-checked:after:bg-white after:content-[''] after:absolute after:top-[4px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-customBgDark"></div>
                    </label>
                  </div>

                  <div className="flex justify-between">
                    <p>Index</p>
                    <label className="inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={isChecked}
                        onChange={handleCheckboxChange}
                      />
                      <div className="relative w-12 h-7 bg-customBg peer-focus:outline-none rounded-full peer dark:bg-customBg peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white peer-checked:after:bg-white after:content-[''] after:absolute after:top-[4px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-customBgDark"></div>
                    </label>
                  </div>

                  <div className="flex justify-between">
                    <p>ReIndex</p>
                    <label className="inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={isChecked1}
                        onChange={handleCheckboxChange1}
                      />
                      <div className="relative w-12 h-7 bg-customBg peer-focus:outline-none rounded-full peer dark:bg-customBg peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white peer-checked:after:bg-white after:content-[''] after:absolute after:top-[4px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-customBgDark"></div>
                    </label>
                  </div>

                  <div className="grid grid-cols-1 gap-6">
                    <div className="flex justify-between items-center">
                      <p>Archived chats</p>
                      <button className="bg-customGray py-2 px-4 rounded-[10px]">Manage</button>
                    </div>

                    <div className="flex justify-between items-center">
                      <p>Archive all chats</p>
                      <button className="bg-customGray py-2 px-4 rounded-[10px]">Archive Al</button>
                    </div>

                    <div className="flex justify-between items-center">
                      <p>Delete all chats</p>
                      <button className="bg-[#E84141] text-white py-2 px-4 rounded-[10px] min-w-[105px] ">
                        Delete All
                      </button>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <p>Chat history & training</p>
                    <label className="inline-flex items-center cursor-pointer">
                      <input type="checkbox" value="" className="sr-only peer" />
                      <div className="relative w-12 h-7 bg-customBg peer-focus:outline-none rounded-full peer dark:bg-customBg peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white peer-checked:after:bg-white after:content-[''] after:absolute after:top-[4px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-customBgDark"></div>
                    </label>
                  </div>

                  <div className="flex justify-between items-center">
                    <p>Delete Account</p>
                    <button className="bg-[#E84141] text-white py-2 px-4 rounded-[10px]">Delete</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <Link to="/privacy" className="text-[#959CB6] text-[16px] absolute bottom-4 right-8">
        Privacy Policy
      </Link>
    </>
  );
};

export default Settings;
