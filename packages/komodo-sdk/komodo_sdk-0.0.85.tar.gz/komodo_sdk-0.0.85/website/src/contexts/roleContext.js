import { createContext, useEffect, useState } from "react";
import { ApiGet, ApiPost } from "../API/API_data";
import { API_Path } from "../API/ApiComment";
import { ErrorToast } from "../helpers/Toast";
import axios from "axios";

const Context = createContext("");

export function RoleStore(props) {
  const [reactSelect, setReactSelect] = useState();
  const [user, setUser] = useState("");
  const [agentList, setAgentList] = useState();
  const [list, setList] = useState([]);
  const [chatHistory, setChatHistory] = useState(false);
  const [chatGuid, setChatGuid] = useState("");
  const [chatRes, setChatRes] = useState("");
  const [company, setCompany] = useState("");
  const [agentType, setAgentType] = useState("");
  const [filesData, setFilesData] = useState({});
  const [pdfData, setPdfData] = useState("");
  const [pdfURL, setPdfURL] = useState("")
  // console.log("pdfData :>> ", pdfData);
  // const [firstPdfData, setFirstPdfData] = useState("");

  useEffect(() => {
    if (user === "") {
      set_user_login_data();
    }
    if (user !== "") {
      agentDetails();
    }
  }, [user]);

  useEffect(() => {
    if (user !== "") {
      conversations();
    }
  }, [reactSelect?.shortcode]);

  const set_user_login_data = () => {
    const userDetails = JSON.parse(localStorage.getItem("komodoUser"));
    setUser(userDetails?.email || "");

    const r = document.querySelector(":root");
    r.style.setProperty("--primary-color", userDetails?.color || "#316FF6");
    r.style.setProperty("--secondary-color", userDetails?.bgcolor || "#F2F6FF");
    r.style.setProperty("--dark-color", userDetails?.bgdark || "#2E2E2E");
  };

  const agentDetails = async () => {
    const user = JSON.parse(localStorage.getItem("komodoUser"));
    try {
      const agent = await ApiGet(API_Path.applianceDescriptionUrl);
      if (agent?.status === 200) {
        setAgentList(agent?.data);
        localStorage.setItem(
          "komodoUser",
          JSON.stringify({
            ...user,
            select: user.select || agent?.data?.agents[0],
          })
        );
        setReactSelect(user.select || agent?.data?.agents[0]);
      }
    } catch (error) {
      console.log("user details get ::error", error);
      ErrorToast(error?.data?.detail || "Something went wrong");
    }
  };

  const conversations = async (flag) => {
    try {
      const agent = await ApiGet(
        API_Path.agentConversationsGetUrl(reactSelect?.shortcode)
      );
      if (agent?.status === 200) {
        let sortedArray = agent?.data.sort((item1, item2) => {
          return new Date(item2.createdAt) - new Date(item1.createdAt);
        });

        setList(sortedArray);
        if (flag === true) {
          setChatGuid(sortedArray[0]?.guid);
        }
      }
    } catch (error) {
      console.log("user details get ::error", error);
      setList([]);
      ErrorToast(error?.data?.detail || "Something went wrong");
    }
  };

  const getUserFiles = async (shortcode) => {
    try {
      const files = await ApiGet(
        API_Path.collectionsGetCollectionUrl(shortcode)
      );
      setFilesData(files?.data);
      // setFirstPdfData(files?.data?.files[0]);
    } catch (error) {
      console.log("error", error);
    }
  };

  const companyData = async () => {
    try {
      const agent = await ApiGet(API_Path.applianceDescriptionUrl);
      setCompany(agent?.data?.company);
      setAgentType(agent?.data);
    } catch (error) {
      console.log("user details get ::error", error);
    }
  };

  useEffect(() => {
    companyData();
  }, []);

  const handleFileData = async (id, guid, type) => {
    console.log('typeasds', type);
    try {
      // if (type === "application/pdf") {
      //   const file = await ApiGet(
      //     API_Path.collectionsDownloadFileUrl(id, guid)
      //   );
      //   // console.log("file?.data :>> ", file?.data);
      //   setPdfData(file?.data);
      // } else {
      //   const file = await ApiGet(
      //     API_Path.collectionsDownloadFileUrl(id, guid) + "/text"
      //   );
      //   // console.log("file?.data :>> ", file?.data);
      //   setPdfData(file?.data);
      // }

      //old one
      // const file = await ApiGet(API_Path.collectionsDownloadFileUrl(id, guid));
      // console.log('file', file);
      // setPdfURL(window.location.origin + API_Path.collectionsDownloadFileUrl(id, guid))
      // setPdfData(file?.data);

      // with blob URL
      const authUser = JSON.parse(localStorage.getItem('komodoUser'))
      const response = await axios.get(
        API_Path.collectionsDownloadFileUrl(id, guid),
        {
          headers: {
            "Content-Type": "application/json",
            "X-User-Email": authUser?.email,
          },
          responseType: 'blob', // Important
        }
      );
      console.log('response.data', response);
      const blob = new Blob([response.data], { type });
      const blobUrl = URL.createObjectURL(blob);
      console.log('blobUrl ', blobUrl);
      setPdfURL(blobUrl)
    } catch (error) {
      console.log("user details get ::error", error);
    }
  };

  return (
    <Context.Provider
      value={{
        reactSelect,
        agentList,
        list,
        chatHistory,
        chatGuid,
        chatRes,
        filesData,
        company,
        agentType,
        pdfData,
        pdfURL,
        ...{
          setReactSelect,
          setUser,
          setList,
          setChatHistory,
          conversations,
          setChatGuid,
          setChatRes,
          getUserFiles,
          handleFileData,
          setFilesData
        },
      }}
    >
      {props.children}
    </Context.Provider>
  );
}

export default Context;
