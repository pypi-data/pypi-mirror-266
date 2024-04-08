import React, { useContext, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import PrimaryLayout from "../../layout/PrimaryLayout";
import profile from "../../images/profile.png";
import wave from "../../images/wave.png";
import send from "../../images/send.png";
import dots from "../../images/dots.png";
import roleContext from "../../contexts/roleContext";
import { ErrorToast } from "../../helpers/Toast";
import { ApiGet } from "../../API/API_data";
import { API_Path } from "../../API/ApiComment";
import EnhancedPrompt from "./EnhancedPrompt";

const Details = () => {
  const context = useContext(roleContext);
  const [prompt, setPrompt] = useState("");
  const [text, setText] = useState("");
  const [allChatData, setAllChatData] = useState([]);
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem("komodoUser"));
  const [loader, setLoader] = useState(false);
  const [newDetails, setNewDetails] = useState({ gId: "", chatRes: "" });

  useEffect(() => {
    if (location?.pathname) {
      getConversationByGuid(location.pathname.split("/details/")[1]);
      setNewDetails({
        ...newDetails,
        gId: location.pathname.split("/details/")[1],
      });
    }
  }, [location?.pathname]);

  const getConversationByGuid = async (guid) => {
    try {
      setLoader(true);
      const res = await ApiGet(API_Path.conversationsGetUrl(guid));
      if (res?.status === 200) {
        setAllChatData(res?.data[0]?.messages);
      }
    } catch (error) {
      console.log("user details get ::error", error);
      ErrorToast(error?.data?.detail || "Something went wrong");
    } finally {
      setLoader(false);
    }
  };

  const sendPrompt = async () => {
    if (newDetails.chatRes !== "") {
      setAllChatData((prevData) => [
        ...prevData,
        { sender: context?.reactSelect?.shortcode, text: newDetails.chatRes },
        { sender: user.email, text: prompt },
      ]);
      setNewDetails({ ...newDetails, chatRes: "" });
    } else {
      setAllChatData((prevData) => [
        ...prevData,
        { sender: user.email, text: prompt },
      ]);
    }

    setText(prompt);
    setPrompt("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      sendPrompt();
    }
  };

  return (
    <PrimaryLayout>
      <div className="w-full flex items-center flex-col">
        <div className="mt-10 mx-8 h-[calc(100vh-218px)] overflow-y-auto scrollbar w-[1017px] xl:w-[950px] lg:w-[800px] md:w-auto md:mx-4 sm:mx-2">
          {loader ? (
            <div className="h-full bg-white"></div>
          ) : (
            <>
              {allChatData && allChatData.length > 0 ? (
                allChatData.map((val, i) => {
                  return (
                    <div className="mb-10" key={i}>
                      {val?.sender === user.email && (
                        <div div className="flex gap-5 items-center">
                          <div>
                            <img
                              src={profile}
                              alt="profile"
                              className="w-[30px] h-[30px]"
                            />
                          </div>
                          <div className="text-[16px] font-cerebriregular rounded-md bg-[#497ad32b] px-4 py-3 text-customBlue">
                            {val?.text}
                          </div>
                        </div>
                      )}
                      {val?.sender === context?.reactSelect?.shortcode && (
                        <div>
                          <div className="mt-10 flex gap-5">
                            <div>
                              <img
                                src={wave}
                                alt="wave"
                                className="w-[30px] h-[30px]"
                              />
                            </div>
                            <div className="w-fit text-[#495057]  md:break-all ">
                              <p
                                className="font-cerebriregular text-[15px] leading-[34px] text-justify"
                                dangerouslySetInnerHTML={{ __html: val?.text }}
                              ></p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })
              ) : (
                <div className="flex justify-center items-center h-full">
                  <div className="text-2xl font-cerebriregular text-[#495057] ">
                    No Conversation Found
                  </div>
                </div>
              )}
              {text !== "" && (
                <div className="mb-10">
                  <div>
                    <div className="mt-10 flex gap-5">
                      <div>
                        <img
                          src={wave}
                          alt="wave"
                          className="w-[30px] h-[30px] "
                        />
                      </div>
                      <div className="w-fit text-[#495057] md:break-all">
                        <EnhancedPrompt
                          prompt={text}
                          guid={newDetails?.gId}
                          setNewDetails={setNewDetails}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <div className="flex gap-4 items-center justify-center  py-5 border-t-[0.5px] border-[#CDCDCD] w-full lg:w-[800px] mx-8 md:w-[700px] md:mx-4 sm:w-[400px] sm:mx-2 xxs:w-[350px]">
          <div className="w-[14px] sm:w-[40px]">
            <img src={dots} alt="send" />
          </div>
          <input
            type="text"
            placeholder="Ask me anything..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyPress}
            className="w-[892px] h-[43px] border border-[#CFD4D8] rounded-md px-4 text-[14px] font-cerebriregular leading-[17.78px] outline-none "
          />
          <img
            src={send}
            alt="send"
            onClick={sendPrompt}
            className="cursor-pointer w-[44px] h-[43px]"
          />
        </div>
      </div>
    </PrimaryLayout>
  );
};

export default Details;
