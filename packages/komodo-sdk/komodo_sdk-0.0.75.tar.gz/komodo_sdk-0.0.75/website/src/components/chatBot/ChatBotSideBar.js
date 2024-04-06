import React, { useContext, useEffect, useRef, useState } from "react";
import odtIcon from "../../assets/odt.png";
import dots from "../../images/dots.png";
import arrowLeft from "../../assets/arrowLeft.svg";
import { ApiDelete, ApiGet, ApiPost } from "../../API/API_data";
import { API_Path } from "../../API/ApiComment";
import { Box, Modal } from "@mui/material";
import { ErrorToast, SuccessToast } from "../../helpers/Toast";
import { useLocation, useNavigate } from "react-router";
import roleContext from "../../contexts/roleContext";
import { FiDownloadCloud } from "react-icons/fi";
import axios from "axios";
import { IoIosClose } from "react-icons/io";
import pdf from "../../images/pdf.png";
import word from "../../images/word.png";
import txt from "../../images/txt.png";
import { AiOutlineCloudUpload } from "react-icons/ai";

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
  borderRadius: "20px",
  outline: "none",
};

const ChatBotSideBar = ({
  uploadedFiles = [],
  setIsCollections,
  isCollections,
  setSelectedCollectionName,
  setSelectedFileName,
  // filesData,
  // setFilesData,
  // getUserFiles,
}) => {
  const user = JSON.parse(localStorage.getItem("komodoUser"));
  const fileInputRef = useRef(null);

  const [open, setOpen] = useState(false);

  const [collection, setCollection] = useState("");
  const [description, setDescription] = useState("");
  // const [fileData, setFileData] = useState("");
  // console.log("fileData :>> ", fileData);
  const [collectName, setCollectName] = useState("");
  const [collect, setCollect] = useState([]);
  const [deleteChat, setDeleteChat] = useState(false);
  const [deleteChatId, setDeleteChatId] = useState(null);
  const [deleteChat1, setDeleteChat1] = useState(false);
  const [deleteChatId1, setDeleteChatId1] = useState(null);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);
  const navigate = useNavigate();
  const contextFiles = useContext(roleContext);
  const location = useLocation();
  const pathnameParts = location.pathname.split("/");
  const id = pathnameParts[pathnameParts.length - 1];
  const listData = useContext(roleContext);
  const [activeTab, setActiveTab] = useState(1);

  const changeTab = (tabIndex) => {
    setActiveTab(tabIndex);
  };

  const collections = [
    "abc",
    "xyz",
    "dots",
    "dolor",
    "large text",
    "test folder",
  ];

  const handleDelete = (chatId, e) => {
    e.stopPropagation();
    setDeleteChat(true);
    setDeleteChatId(chatId);
  };

  const handleClickOutside = (e) => {
    // if (modalRef.current && !modalRef?.current?.contains(e.target)) {
    //   setDeleteChat(false);
    // }
    if (!["close", "close1"].includes(e?.target?.id)) {
      setDeleteChat(false);
      setDeleteChat1(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    CollectionData();
  }, []);

  const CollectionData = async () => {
    try {
      const collection = await ApiGet(API_Path.collectionsGetUrl);
      setCollect(collection?.data);
    } catch (error) {
      console.log("error", error);
    }
  };

  const getFileIcon = (fileType, path) => {
    if (fileType?.includes("pdf")) {
      return (
        // <svg
        //   width="20"
        //   height="20"
        //   viewBox="0 0 43 43"
        //   fill="none"
        //   xmlns="http://www.w3.org/2000/svg"
        // >
        //   <path
        //     d="M39.3829 11.3381L28.3937 0.348871C28.1972 0.1524 27.9306 0.0420192 27.6527 0.0419922H15.3449C8.70895 0.0419922 3.31026 5.44177 3.31026 12.0791V27.1549C3.31026 27.7337 3.7794 28.2028 4.35814 28.2028C4.93687 28.2028 5.40601 27.7337 5.40601 27.1549V12.0791C5.40601 6.59739 9.86457 2.13774 15.345 2.13774H26.6049V6.57144C26.6049 10.1717 29.534 13.1007 33.1343 13.1007H37.5941V30.9234C37.5941 36.4038 33.1345 40.8623 27.6528 40.8623H15.3449C9.86449 40.8623 5.40593 36.4038 5.40593 30.9234C5.40593 30.3446 4.93679 29.8755 4.35805 29.8755C3.77932 29.8755 3.31018 30.3446 3.31018 30.9234C3.31018 37.5593 8.70895 42.958 15.3448 42.958H27.6527C34.29 42.958 39.6898 37.5593 39.6898 30.9234V12.0791C39.6898 11.8011 39.5793 11.5346 39.3829 11.3381ZM28.7006 6.57136V3.61956L36.086 11.005H33.1343C30.6895 11.005 28.7006 9.01614 28.7006 6.57136Z"
        //     fill="var(--primary-color)"
        //   />
        //   <path
        //     d="M17.0071 22.795C17.2345 22.9857 17.4105 23.2313 17.5351 23.532C17.6671 23.8327 17.7331 24.1957 17.7331 24.621C17.7331 25.1197 17.6378 25.578 17.4471 25.996C17.2565 26.4067 16.9595 26.722 16.5561 26.942C16.4021 27.03 16.2371 27.0997 16.0611 27.151C15.8925 27.195 15.7238 27.228 15.5551 27.25C15.3865 27.272 15.2251 27.2867 15.0711 27.294C14.9171 27.294 14.7778 27.294 14.6531 27.294H13.8391V30H12.0241V22.157H14.6531C15.2251 22.157 15.6945 22.212 16.0611 22.322C16.4351 22.4247 16.7505 22.5823 17.0071 22.795ZM15.5771 25.545C15.8045 25.3837 15.9181 25.1123 15.9181 24.731C15.9181 24.5257 15.8851 24.357 15.8191 24.225C15.7605 24.0857 15.6761 23.9757 15.5661 23.895C15.4121 23.7923 15.2251 23.73 15.0051 23.708C14.7925 23.686 14.5908 23.675 14.4001 23.675H13.8391V25.776H14.4001C14.4881 25.776 14.5835 25.776 14.6861 25.776C14.7961 25.7687 14.9025 25.7577 15.0051 25.743C15.1151 25.7283 15.2178 25.7063 15.3131 25.677C15.4158 25.6477 15.5038 25.6037 15.5771 25.545ZM19.2558 30V22.157H21.7418C22.4018 22.157 22.9554 22.2193 23.4028 22.344C23.8574 22.4613 24.2498 22.6373 24.5798 22.872C25.0491 23.2093 25.3974 23.653 25.6248 24.203C25.8594 24.7457 25.9768 25.3727 25.9768 26.084C25.9768 26.7953 25.8594 27.4223 25.6248 27.965C25.3974 28.5077 25.0491 28.9477 24.5798 29.285C24.2498 29.5197 23.8574 29.6993 23.4028 29.824C22.9554 29.9413 22.4018 30 21.7418 30H19.2558ZM21.0708 28.416H21.7308C22.0681 28.416 22.3651 28.3793 22.6218 28.306C22.8858 28.2327 23.1131 28.13 23.3038 27.998C23.5898 27.8073 23.8024 27.5507 23.9418 27.228C24.0884 26.898 24.1618 26.5167 24.1618 26.084C24.1618 25.644 24.0884 25.2627 23.9418 24.94C23.8024 24.61 23.5898 24.3497 23.3038 24.159C22.9078 23.8877 22.3834 23.752 21.7308 23.752H21.0708V28.416ZM32.3891 23.752H29.4411V25.292H31.9821V26.865H29.4411V30H27.6261V22.157H32.3891V23.752Z"
        //     fill="var(--primary-color)"
        //   />
        // </svg>
        <img src={pdf} alt="pdf" />
      );
    } else if (fileType.includes("doc") || fileType.includes("msword")) {
      return (
        // <svg
        //   xmlns="http://www.w3.org/2000/svg"
        //   width="20"
        //   height="20"
        //   viewBox="0 0 43 43"
        //   fill="none"
        // >
        //   <path
        //     d="M39.3829 11.3381L28.3937 0.348871C28.1972 0.1524 27.9306 0.0420192 27.6527 0.0419922H15.3449C8.70895 0.0419922 3.31026 5.44177 3.31026 12.0791V27.1549C3.31026 27.7337 3.7794 28.2028 4.35814 28.2028C4.93687 28.2028 5.40601 27.7337 5.40601 27.1549V12.0791C5.40601 6.59739 9.86457 2.13774 15.345 2.13774H26.6049V6.57144C26.6049 10.1717 29.534 13.1007 33.1343 13.1007H37.5941V30.9234C37.5941 36.4038 33.1345 40.8623 27.6528 40.8623H15.3449C9.86449 40.8623 5.40593 36.4038 5.40593 30.9234C5.40593 30.3446 4.93679 29.8755 4.35805 29.8755C3.77932 29.8755 3.31018 30.3446 3.31018 30.9234C3.31018 37.5593 8.70895 42.958 15.3448 42.958H27.6527C34.29 42.958 39.6898 37.5593 39.6898 30.9234V12.0791C39.6898 11.8011 39.5793 11.5346 39.3829 11.3381ZM28.7006 6.57136V3.61956L36.086 11.005H33.1343C30.6895 11.005 28.7006 9.01614 28.7006 6.57136Z"
        //     fill="var(--primary-color)"
        //   />
        //   <path
        //     d="M10.7386 30V22.87H12.9986C13.5986 22.87 14.102 22.9267 14.5086 23.04C14.922 23.1467 15.2786 23.3067 15.5786 23.52C16.0053 23.8267 16.322 24.23 16.5286 24.73C16.742 25.2233 16.8486 25.7933 16.8486 26.44C16.8486 27.0867 16.742 27.6567 16.5286 28.15C16.322 28.6433 16.0053 29.0433 15.5786 29.35C15.2786 29.5633 14.922 29.7267 14.5086 29.84C14.102 29.9467 13.5986 30 12.9986 30H10.7386ZM12.3886 28.56H12.9886C13.2953 28.56 13.5653 28.5267 13.7986 28.46C14.0386 28.3933 14.2453 28.3 14.4186 28.18C14.6786 28.0067 14.872 27.7733 14.9986 27.48C15.132 27.18 15.1986 26.8333 15.1986 26.44C15.1986 26.04 15.132 25.6933 14.9986 25.4C14.872 25.1 14.6786 24.8633 14.4186 24.69C14.0586 24.4433 13.582 24.32 12.9886 24.32H12.3886V28.56ZM21.718 30.14C21.178 30.14 20.6813 30.05 20.228 29.87C19.7813 29.69 19.3947 29.44 19.068 29.12C18.748 28.7933 18.4947 28.4033 18.308 27.95C18.128 27.49 18.038 26.9867 18.038 26.44C18.038 25.8867 18.128 25.3833 18.308 24.93C18.4947 24.4767 18.748 24.0867 19.068 23.76C19.3947 23.4333 19.7813 23.18 20.228 23C20.6813 22.82 21.178 22.73 21.718 22.73C22.2513 22.73 22.7413 22.82 23.188 23C23.6413 23.18 24.0313 23.4333 24.358 23.76C24.6847 24.0867 24.938 24.4767 25.118 24.93C25.298 25.3833 25.388 25.8867 25.388 26.44C25.388 26.9867 25.298 27.49 25.118 27.95C24.938 28.4033 24.6847 28.7933 24.358 29.12C24.0313 29.44 23.6413 29.69 23.188 29.87C22.7413 30.05 22.2513 30.14 21.718 30.14ZM21.718 28.63C22.0113 28.63 22.2813 28.58 22.528 28.48C22.7747 28.3733 22.988 28.2233 23.168 28.03C23.348 27.8367 23.488 27.6067 23.588 27.34C23.688 27.0667 23.738 26.7667 23.738 26.44C23.738 26.1067 23.688 25.8067 23.588 25.54C23.488 25.2667 23.348 25.0367 23.168 24.85C22.988 24.6567 22.7747 24.5067 22.528 24.4C22.2813 24.2933 22.0113 24.24 21.718 24.24C21.4247 24.24 21.1513 24.2933 20.898 24.4C20.6513 24.5067 20.438 24.6567 20.258 24.85C20.078 25.0367 19.938 25.2667 19.838 25.54C19.738 25.8067 19.688 26.1067 19.688 26.44C19.688 26.7667 19.738 27.0667 19.838 27.34C19.938 27.6067 20.078 27.8367 20.258 28.03C20.438 28.2233 20.6513 28.3733 20.898 28.48C21.1513 28.58 21.4247 28.63 21.718 28.63ZM30.2258 30.14C29.6858 30.14 29.1892 30.05 28.7358 29.87C28.2892 29.69 27.9025 29.44 27.5758 29.12C27.2558 28.7933 27.0025 28.4033 26.8158 27.95C26.6358 27.49 26.5458 26.9867 26.5458 26.44C26.5458 25.8867 26.6358 25.3833 26.8158 24.93C27.0025 24.4767 27.2558 24.0867 27.5758 23.76C27.9025 23.4333 28.2892 23.18 28.7358 23C29.1892 22.82 29.6858 22.73 30.2258 22.73C30.6392 22.73 31.0258 22.7867 31.3858 22.9C31.7458 23.0067 32.0725 23.16 32.3658 23.36C32.6658 23.56 32.9258 23.8033 33.1458 24.09C33.3658 24.37 33.5358 24.6867 33.6558 25.04L32.1058 25.59C31.9725 25.17 31.7392 24.84 31.4058 24.6C31.0725 24.36 30.6792 24.24 30.2258 24.24C29.9325 24.24 29.6592 24.2933 29.4058 24.4C29.1592 24.5067 28.9458 24.6567 28.7658 24.85C28.5858 25.0367 28.4458 25.2667 28.3458 25.54C28.2458 25.8067 28.1958 26.1067 28.1958 26.44C28.1958 26.7667 28.2458 27.0667 28.3458 27.34C28.4458 27.6067 28.5858 27.8367 28.7658 28.03C28.9458 28.2233 29.1592 28.3733 29.4058 28.48C29.6592 28.58 29.9325 28.63 30.2258 28.63C30.6792 28.63 31.0725 28.51 31.4058 28.27C31.7392 28.03 31.9725 27.7 32.1058 27.28L33.6558 27.83C33.5358 28.1833 33.3658 28.5033 33.1458 28.79C32.9258 29.07 32.6658 29.31 32.3658 29.51C32.0725 29.71 31.7458 29.8667 31.3858 29.98C31.0258 30.0867 30.6392 30.14 30.2258 30.14Z"
        //     fill="var(--primary-color)"
        //   />
        // </svg>
        <img src={word} alt="word" />
      );
    } else if (fileType.includes("text")) {
      return (
        // <svg
        //   xmlns="http://www.w3.org/2000/svg"
        //   width="20"
        //   height="20"
        //   viewBox="0 0 43 43"
        //   fill="none"
        // >
        //   <path
        //     d="M39.3829 11.3381L28.3937 0.348871C28.1972 0.1524 27.9306 0.0420192 27.6527 0.0419922H15.3449C8.70895 0.0419922 3.31026 5.44177 3.31026 12.0791V27.1549C3.31026 27.7337 3.7794 28.2028 4.35814 28.2028C4.93687 28.2028 5.40601 27.7337 5.40601 27.1549V12.0791C5.40601 6.59739 9.86457 2.13774 15.345 2.13774H26.6049V6.57144C26.6049 10.1717 29.534 13.1007 33.1343 13.1007H37.5941V30.9234C37.5941 36.4038 33.1345 40.8623 27.6528 40.8623H15.3449C9.86449 40.8623 5.40593 36.4038 5.40593 30.9234C5.40593 30.3446 4.93679 29.8755 4.35805 29.8755C3.77932 29.8755 3.31018 30.3446 3.31018 30.9234C3.31018 37.5593 8.70895 42.958 15.3448 42.958H27.6527C34.29 42.958 39.6898 37.5593 39.6898 30.9234V12.0791C39.6898 11.8011 39.5793 11.5346 39.3829 11.3381ZM28.7006 6.57136V3.61956L36.086 11.005H33.1343C30.6895 11.005 28.7006 9.01614 28.7006 6.57136Z"
        //     fill="var(--primary-color)"
        //   />
        //   <path
        //     d="M17.6549 22.157V23.752H15.8289V30H14.0139V23.752H12.1879V22.157H17.6549ZM18.3548 30L21.4238 25.919L18.4208 22.157H20.6318L22.5018 24.588L24.3718 22.157H26.5828L23.5798 25.919L26.6488 30H24.3718L22.5018 27.415L20.6318 30H18.3548ZM32.8272 22.157V23.752H31.0012V30H29.1862V23.752H27.3602V22.157H32.8272Z"
        //     fill="var(--primary-color)"
        //   />
        // </svg>
        <img src={txt} alt="txt" />
      );
    } else {
      return <img src={odtIcon} alt="txt" />;
    }
  };

  const handleSelectItem = (name) => {
    setSelectedCollectionName(name);
  };

  const handleSelectedFileName = (name) => {
    setSelectedFileName(name);
  };

  // const handleButtonClick = () => {
  //   fileInputRef.current.click();
  // };

  const handleAddCollections = async () => {
    let body = {
      name: collection,
      description: description,
    };
    try {
      const response = await ApiPost(API_Path.collectionsAddUrl, body);
      if (response.status === 200) {
        // Handle success
        SuccessToast("Collection added successfully");
        setOpen(false);
        setCollection("");
        setDescription("");
        CollectionData();
      } else {
        // Handle error
        ErrorToast("Failed to add collection");
      }
    } catch (error) {
      console.error("Error occurred while adding collection:", error);
    }
  };

  // const handleFileChange = (e) => {
  //   const file = e.target.files[0];
  //   // console.log("Uploaded file:", file);
  // };

  const handleFileChange = async (event) => {
    const selectedFile = event.target.files[0];
    console.log("Selected file:", selectedFile);

    let formData = new FormData();
    formData.append("files", selectedFile);

    try {
      const user = JSON.parse(localStorage.getItem("komodoUser"));

      let headers = {
        "Content-Type": "multipart/form-data",
        "X-User-Email": user?.email,
      };
      axios
        .post(API_Path.collectionsUploadFilesUrl(id), formData, {
          headers: headers,
        })
        .then((response) => {
          contextFiles?.getUserFiles(id);
          SuccessToast("File uploaded successfully");
        })
        .catch((err) => {
          console.log("err :>> ", err);
        });
    } catch (error) {
      console.error("Error occurred while adding collection:", error);
    }
  };

  const handleFileDelete = async (fileId, e) => {
    e.stopPropagation();
    setDeleteChat1(true);
    setDeleteChatId1(fileId);
  };

  const handleFileChatDelete = async (fileId, e) => {
    console.log('fileId :>> ', fileId);
    console.log('id :>> ', id);
    e.stopPropagation();
    try {
      const file = await ApiDelete(`${API_Path.collectionsGetUrl}/${id}/${fileId}`);
      // console.log('file :>> ', file);
      if (file?.status === 200) {
        SuccessToast("Deleted successfully");
        const remainingData = await contextFiles?.filesData?.files?.filter((v) => fileId !== v?.guid)
        contextFiles?.setFilesData({ ...contextFiles?.filesData, files: remainingData })
      }
    } catch (error) {
      console.log("user details get ::error", error);
      ErrorToast(error?.data?.detail || "Something went wrong");
    }
  };

  // useEffect(() => {
  //   const handleOutsideClick = (e) => {
  //     if (showModal && !e.target.closest(".modal")) {
  //       setShowModal(false);
  //     }
  //   };

  //   document.body.addEventListener("click", handleOutsideClick);

  //   return () => {
  //     document.body.removeEventListener("click", handleOutsideClick);
  //   };
  // }, [showModal]);

  const handleChatDelete = async (id, e) => {
    e.stopPropagation();
    try {
      const file = await ApiDelete(API_Path.collectionsDeleteCollectionUrl(id));
      if (file?.status === 200) {
        SuccessToast("Deleted successfully");
        setDeleteChat(false);
        CollectionData();
      }
    } catch (error) {
      console.log("user details get ::error", error);
    }
  };

  // const fileInputRef = useRef(null);

  const uploadFile = async () => {
    fileInputRef.current.value = null;
    fileInputRef.current.click();
  };

  // const handleFileData = async (guid) => {
  //   try {
  //     const file = await ApiGet(API_Path.collectionsDownloadFileUrl(id, guid));
  //     console.log("file?.data :>> ", file?.data);
  //     setFileData(file?.data);
  //   } catch (error) {
  //     console.log("user details get ::error", error);
  //   }
  // };

  const handleDetails = (val) => {
    navigate(`/details/${val?.guid}`);
  };

  const formatDate = (date) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    const valDate = new Date(date);
    if (valDate.toDateString() === today.toDateString()) {
      return "Today";
    } else if (valDate.toDateString() === yesterday.toDateString()) {
      return "Yesterday";
    } else {
      return "Previous";
    }
  };
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const toggleDrawer = () => {
    setIsDrawerOpen(!isDrawerOpen);
  };

  const renderChatItems = () => {
    let todayDisplayed = false;
    let yesterdayDisplayed = false;
    let previousDisplayed = false;
    return listData?.list?.map((val, i) => {
      const formattedDate = formatDate(val?.createdAt);

      if (formattedDate === "Today" && !todayDisplayed) {
        todayDisplayed = true;
        return (
          <React.Fragment key={`today-${i}`}>
            <div
              className={`px-5 border-b-[0.5px] border-[#F6F6F9] py-5 text-[#C5C5C5] text-[12px] font-cerebri leading-[15.24px] tracking-[2px] uppercase`}
            >
              Today
            </div>
            {renderChatItem(val, i)}
          </React.Fragment>
        );
      } else if (formattedDate === "Yesterday" && !yesterdayDisplayed) {
        yesterdayDisplayed = true;
        return (
          <React.Fragment key={`yesterday-${i}`}>
            <div
              className={`px-5 border-b-[0.5px] border-[#F6F6F9] py-5 text-[#C5C5C5] text-[12px] font-cerebri leading-[15.24px] tracking-[2px] uppercase`}
            >
              Yesterday
            </div>
            {renderChatItem(val, i)}
          </React.Fragment>
        );
      } else if (formattedDate === "Previous" && !previousDisplayed) {
        previousDisplayed = true;
        return (
          <React.Fragment key={`previous-${i}`}>
            <div
              className={`px-5 border-b-[0.5px] border-[#F6F6F9] py-5 text-[#C5C5C5] text-[12px] font-cerebri leading-[15.24px] tracking-[2px] uppercase`}
            >
              Previous
            </div>
            {renderChatItem(val, i)}
          </React.Fragment>
        );
      } else {
        return renderChatItem(val, i);
      }
    });
  };

  const renderChatItem = (val, i) => (
    <div
      key={val?.guid}
      // onClick={() => handleDetails(val)}
      className={`px-5 border-b-[0.5px] border-[#F6F6F9] py-5 text-[#5A636C] text-[14px] leading-[17.78px] flex justify-between items-center font-cerebriregular cursor-pointer ${id === val?.guid ? "bg-[#F6F6F9]" : ""
        }`}
    >
      <div className="flex items-center gap-3">
        <span className="bg-customBg p-2 rounded-[5px]">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="19"
            height="19"
            viewBox="0 0 22 22"
            fill="none"
          >
            <path
              d="M20.804 9.35881V14.2485C20.804 19.1382 18.8432 21.0941 13.9412 21.0941H8.05888C3.15692 21.0941 1.19614 19.1382 1.19614 14.2485V8.38087C1.19614 3.49116 3.15692 1.53528 8.05888 1.53528H12.9608"
              stroke="var(--primary-color)"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <path
              d="M20.804 9.35881H16.8824C13.9412 9.35881 12.9608 8.38087 12.9608 5.44704V1.53528L20.804 9.35881Z"
              stroke="var(--primary-color)"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <path
              d="M6.09802 12.2927H11.9804"
              stroke="var(--primary-color)"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <path
              d="M6.09802 16.2045H10.0196"
              stroke="var(--primary-color)"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        {/* <span className='bg-[#eee5dc] p-1 rounded-full'>
                    
              
                    <img src={chatListIcon}/>
                </span> */}

        <div
          className="w-[200px] lg:w-[110px] xl:w-[60px] xxl:w-[100px] truncate"
          onClick={() => setIsDrawerOpen(false)}
        >
          {val?.title}
        </div>
      </div>
      <div className="relative">
        <img
          src={dots}
          alt="dots"
          className="min-w-[16px]"
          onClick={(e) => handleDelete(val?.guid, e)}
        />
        {deleteChat && deleteChatId === val?.guid && (
          <div
            // ref={modalRef}
            id="close"
            className="absolute bg-white border rounded-md shadow-md text-center right-0"
            onClick={(e) => handleChatDelete(val?.guid, i, e)}
          >
            <button
              id="close1"
              className="text-[#5A636C] text-[13px] font-cerebri leading-[30px] px-4 py-[2px] mt-1 cursor-pointer"
            >
              Delete
            </button>
          </div>
        )}
      </div>
    </div>
  );

  const [dragging, setDragging] = useState(false);
  const [fileName, setFileName] = useState("");

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);

    const files = [...e.dataTransfer.files];
    if (files.length > 0) {
      // setFileName(files[0].name);

      // let formData = new FormData();
      // formData.append("files", fileName);

      const file = files[0];
      setFileName(file.name);

      let formData = new FormData();
      formData.append("files", file);

      try {
        const user = JSON.parse(localStorage.getItem("komodoUser"));

        let headers = {
          "Content-Type": "multipart/form-data",
          "X-User-Email": user?.email,
        };
        axios
          .post(API_Path.collectionsUploadFilesUrl(id), formData, {
            headers: headers,
          })
          .then((response) => {
            contextFiles?.getUserFiles(id);
            setFileName("");
            SuccessToast("File uploaded successfully");
          })
          .catch((err) => {
            console.log("err :>> ", err);
          });
      } catch (error) {
        console.error("Error occurred while adding collection:", error);
      }
    }
  };

  return (
    <div className="col-span-1 w-[100%]">
      <div>
        <h1 className="text-[21px] font-cerebri text-[#495057] leading-[27px] mt-5 mx-5 mb-5 xxl:text-[18px]">
          Chat with Documents
        </h1>
        {/* {isCollections ? ( */}

        {isCollections ? (
          <div className="text-center">
            <button
              className="bg-customBgDark text-[#fff] rounded-md px-[75px] pb-2 pt-3 text-[15px] font-cerebriregular xxl:px-10 mb-8"
              // onClick={(e) => {
              //   e.stopPropagation();
              //   handleOpenModal();
              // }}
              onClick={handleOpen}
            >
              New Collection
            </button>
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: "none" }}
              onChange={handleFileChange}
            />
          </div>
        ) : (
          // <div className="text-center">
          //   <button className="bg-customBgDark text-[#fff] rounded-md px-[75px] pb-2 pt-3 text-[15px] font-cerebriregular xxl:px-10">
          //     New Document
          //   </button>
          // </div>
          // <div className="h-[140px]">
          //   <div className={`flex items-center gap-2 cursor-pointer px-5`}>
          //     <input
          //       type="file"
          //       ref={fileInputRef}
          //       style={{ display: "none" }}
          //       onChange={handleFileChange}
          //     />
          //     <div
          //       onClick={uploadFile}
          //       className="flex items-center gap-2 cursor-pointer"
          //     >
          //       <span className="bg-customBg p-2 rounded-[5px]">
          //         <svg
          //           width="20"
          //           height="20"
          //           viewBox="0 0 24 24"
          //           fill="none"
          //           xmlns="http://www.w3.org/2000/svg"
          //         >
          //           <path
          //             d="M21.67 14.3L21.27 19.3C21.12 20.83 21 22 18.29 22H5.71001C3.00001 22 2.88001 20.83 2.73001 19.3L2.33001 14.3C2.25001 13.47 2.51001 12.7 2.98001 12.11C2.99001 12.1 2.99001 12.1 3.00001 12.09C3.55001 11.42 4.38001 11 5.31001 11H18.69C19.62 11 20.44 11.42 20.98 12.07C20.99 12.08 21 12.09 21 12.1C21.49 12.69 21.76 13.46 21.67 14.3Z"
          //             stroke="var(--primary-color)"
          //             stroke-width="1.5"
          //             stroke-miterlimit="10"
          //           />
          //           <path
          //             d="M3.5 11.43V6.28C3.5 2.88 4.35 2.03 7.75 2.03H9.02C10.29 2.03 10.58 2.41 11.06 3.05L12.33 4.75C12.65 5.17 12.84 5.43 13.69 5.43H16.24C19.64 5.43 20.49 6.28 20.49 9.68V11.47"
          //             stroke="var(--primary-color)"
          //             stroke-width="1.5"
          //             stroke-miterlimit="10"
          //             stroke-linecap="round"
          //             stroke-linejoin="round"
          //           />
          //           <path
          //             d="M9.43005 17H14.5701"
          //             stroke="var(--primary-color)"
          //             stroke-width="1.5"
          //             stroke-miterlimit="10"
          //             stroke-linecap="round"
          //             stroke-linejoin="round"
          //           />
          //         </svg>
          //       </span>

          //       <div>
          //         <div className="text-blackText font-medium font-cerebriregular text-[16px] w-[110px] whitespace-nowrap overflow-hidden text-ellipsis 1xl:text-[14px]">
          //           Upload File
          //         </div>
          //       </div>
          //     </div>
          //   </div>

          //   <div className="flex justify-center items-center gap-2 px-5 mb-2">
          //     <div class="flex-1 h-[1px] bg-[#CFDFE2]"></div>
          //     <div className="flex items-center justify-center mb-1 text-blackText font-medium font-cerebri">
          //       or
          //     </div>
          //     <div class="flex-1 h-[1px] bg-[#CFDFE2]"></div>
          //   </div>

          //   <div
          //     className={`flex items-center gap-2 cursor-pointer mb-3 px-2 bg-customBg mx-5 rounded-[8px] py-2 1xl:mb-1 text-blackText font-medium font-cerebriregular border-dashed border-2 border-[#BAD1FF] text-[14px]`}
          //   >
          //     <div className="bg-white p-2 rounded-[10px]">
          //       <svg
          //         xmlns="http://www.w3.org/2000/svg"
          //         width="24"
          //         height="24"
          //         viewBox="0 0 24 24"
          //         fill="none"
          //       >
          //         <path
          //           d="M9.31982 6.49994L11.8798 3.93994L14.4398 6.49994"
          //           stroke="#316FF6"
          //           stroke-width="1.5"
          //           stroke-miterlimit="10"
          //           stroke-linecap="round"
          //           stroke-linejoin="round"
          //         />
          //         <path
          //           d="M11.8799 14.18V4.01001"
          //           stroke="#316FF6"
          //           stroke-width="1.5"
          //           stroke-miterlimit="10"
          //           stroke-linecap="round"
          //           stroke-linejoin="round"
          //         />
          //         <path
          //           d="M4 12C4 16.42 7 20 12 20C17 20 20 16.42 20 12"
          //           stroke="#316FF6"
          //           stroke-width="1.5"
          //           stroke-miterlimit="10"
          //           stroke-linecap="round"
          //           stroke-linejoin="round"
          //         />
          //       </svg>
          //     </div>
          //     <div
          //       onDrop={handleDrop}
          //       onDragOver={handleDragOver}
          //       onDragEnter={handleDragEnter}
          //       onDragLeave={handleDragLeave}
          //     >
          //       {fileName ? (
          //         <>
          //           {" "}
          //           {fileName}{" "}
          //           <IoIosClose
          //             onClick={setFileName("")}
          //             className="cursor-pointer"
          //           />{" "}
          //         </>
          //       ) : (
          //         <p>
          //           Drag & Drop or{" "}
          //           <span className="text-customColor"> Browse files </span>
          //         </p>
          //       )}
          //     </div>
          //   </div>
          // </div>
          ""
        )}
      </div>
      {isCollections ? (
        <>
          <div className="flex items-center justify-between pt-4 px-5 border-t-[0.5px] border-[#F6F6F9]">
            <div className="text-blackText text-[18px] mt-4 mb-3 -ml-2 font-cerebriMedium">
              Collections
            </div>
          </div>
          <div>
            <div className="sidebar h-[calc(100vh-251px)] 1xl:h-[calc(100vh-278px)] overflow-auto">
              {collect.map((item, index) => {
                return (
                  <div
                    className={`flex items-center justify-between px-3 py-4 mt-1 cursor-pointer overflow-hidden`}
                    onClick={() => {
                      handleSelectItem(item?.name);
                      setCollectName(item?.name);
                      contextFiles?.getUserFiles(item?.guid);
                      navigate(`/chatdoc/${item?.guid}`, {
                        state: {
                          collectionName: item?.name,
                          // openChat: true,
                          chatId: item?.guid,
                        },
                      });
                    }}
                    key={index}
                  >
                    <div
                      key={index}
                      className={`flex items-center gap-2.5 cursor-pointer`}
                      onClick={() => setIsCollections(false)}
                    >
                      <span className="bg-customBg p-2 rounded-[5px]">
                        <svg
                          width="20"
                          height="20"
                          viewBox="0 0 24 24"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            d="M21.67 14.3L21.27 19.3C21.12 20.83 21 22 18.29 22H5.71001C3.00001 22 2.88001 20.83 2.73001 19.3L2.33001 14.3C2.25001 13.47 2.51001 12.7 2.98001 12.11C2.99001 12.1 2.99001 12.1 3.00001 12.09C3.55001 11.42 4.38001 11 5.31001 11H18.69C19.62 11 20.44 11.42 20.98 12.07C20.99 12.08 21 12.09 21 12.1C21.49 12.69 21.76 13.46 21.67 14.3Z"
                            stroke="var(--primary-color)"
                            stroke-width="1.5"
                            stroke-miterlimit="10"
                          />
                          <path
                            d="M3.5 11.43V6.28C3.5 2.88 4.35 2.03 7.75 2.03H9.02C10.29 2.03 10.58 2.41 11.06 3.05L12.33 4.75C12.65 5.17 12.84 5.43 13.69 5.43H16.24C19.64 5.43 20.49 6.28 20.49 9.68V11.47"
                            stroke="var(--primary-color)"
                            stroke-width="1.5"
                            stroke-miterlimit="10"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                          />
                          <path
                            d="M9.43005 17H14.5701"
                            stroke="var(--primary-color)"
                            stroke-width="1.5"
                            stroke-miterlimit="10"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                          />
                        </svg>
                      </span>

                      <div>
                        <div
                          title={item?.description}
                          className="text-blackText font-cerebriregular text-[16px] capitalize w-[110px] whitespace-nowrap overflow-hidden text-ellipsis"
                        >
                          {item?.name}
                        </div>
                      </div>
                    </div>
                    <div>
                      <img
                        src={dots}
                        alt="dots"
                        className="min-w-[16px]"
                        onClick={(e) => handleDelete(item?.guid, e)}
                      />
                      <div className="absolute">
                        {deleteChat && deleteChatId === item?.guid && (
                          <div
                            id="close"
                            className="relative bg-white border rounded-md shadow-md text-center right-14"
                            onClick={(e) => handleChatDelete(item?.guid, e)}
                          >
                            <button
                              id="close1"
                              className="text-[#5A636C] text-[13px] font-cerebri leading-[30px] px-4 py-[2px] mt-1 cursor-pointer"
                            >
                              Delete
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <h1 className="text-[18px] leading-[25.4px] font-cerebri text-[#495057] ms-5">
            {user?.name}
          </h1>
        </>
      ) : (
        <>
          <div className="py-3 flex flex-col gap-4 border-b border-customGray">
            <div
              className="text-blackText px-5 flex items-center text-[18px] gap-2 -ml-2 font-cerebriMedium cursor-pointer "
              onClick={() => {
                setIsCollections(true);
                setSelectedFileName("");
                navigate(`/chatdoc`);
              }}
            >
              <img src={arrowLeft} className="w-5 h-5" alt="" />
              {/* Collection */}
              <span className="text-blackText text-[18px] font-cerebriMedium capitalize">
                {collectName}
              </span>
            </div>

            <div className="flex justify-center mx-3 xxl:mx-1 bg-customBg rounded-[10px] p-2 w-auto h-[58px] font-cerebriregular">
              <button
                className={`${activeTab === 1
                  ? "bg-white text-customColor"
                  : "bg-transparent"
                  } px-5 py-2 xxl:px-3 sm:text-[16px] cursor-pointer w-full rounded-[10px]`}
                onClick={() => changeTab(1)}
              >
                Files
              </button>
              <button
                className={`${activeTab === 2
                  ? "bg-white text-customColor"
                  : "bg-transparent"
                  } px-5 py-2 xxl:px-3 sm:text-[16px] cursor-pointer w-full rounded-[10px]`}
                onClick={() => changeTab(2)}
              >
                Conversation
              </button>
            </div>

            {/* <span className="text-blackText text-[18px] font-cerebriMedium -ml-2 capitalize">
              {collectName}
            </span> */}
          </div>

          <div>
            {activeTab === 1 && (
              <div className="sidebar h-[calc(100vh-402px)] 1xl:h-[calc(100vh-429px)] overflow-auto">
                {contextFiles?.filesData?.files?.map((val, index) => {
                  return (
                    <div
                      className={` flex items-center justify-between px-3 py-3 mt-1 cursor-pointer overflow-hidden ${val?.guid === location?.state?.fileId
                        ? "bg-[#F6F6F9]"
                        : ""
                        }`}
                      onClick={() => {
                        handleSelectedFileName(val.name);
                        contextFiles?.handleFileData(id, val?.guid, val?.magic);
                        // handleFileData(val?.guid);
                        navigate(`/chatdoc/${id}`, {
                          state: {
                            fileId: val?.guid,
                            // fileData: fileData,
                            fileName: val.name,
                            openChat: true,
                          },
                        });
                      }}
                      key={index}
                    >
                      <div key={index} className={`flex items-center gap-2.5`}>
                        <span className="bg-customBg p-2 rounded-[5px]">
                          {/* <svg
                          width="20"
                          height="20"
                          viewBox="0 0 43 43"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            d="M39.3829 11.3381L28.3937 0.348871C28.1972 0.1524 27.9306 0.0420192 27.6527 0.0419922H15.3449C8.70895 0.0419922 3.31026 5.44177 3.31026 12.0791V27.1549C3.31026 27.7337 3.7794 28.2028 4.35814 28.2028C4.93687 28.2028 5.40601 27.7337 5.40601 27.1549V12.0791C5.40601 6.59739 9.86457 2.13774 15.345 2.13774H26.6049V6.57144C26.6049 10.1717 29.534 13.1007 33.1343 13.1007H37.5941V30.9234C37.5941 36.4038 33.1345 40.8623 27.6528 40.8623H15.3449C9.86449 40.8623 5.40593 36.4038 5.40593 30.9234C5.40593 30.3446 4.93679 29.8755 4.35805 29.8755C3.77932 29.8755 3.31018 30.3446 3.31018 30.9234C3.31018 37.5593 8.70895 42.958 15.3448 42.958H27.6527C34.29 42.958 39.6898 37.5593 39.6898 30.9234V12.0791C39.6898 11.8011 39.5793 11.5346 39.3829 11.3381ZM28.7006 6.57136V3.61956L36.086 11.005H33.1343C30.6895 11.005 28.7006 9.01614 28.7006 6.57136Z"
                            fill="var(--primary-color)"
                          />
                          <path
                            d="M17.0071 22.795C17.2345 22.9857 17.4105 23.2313 17.5351 23.532C17.6671 23.8327 17.7331 24.1957 17.7331 24.621C17.7331 25.1197 17.6378 25.578 17.4471 25.996C17.2565 26.4067 16.9595 26.722 16.5561 26.942C16.4021 27.03 16.2371 27.0997 16.0611 27.151C15.8925 27.195 15.7238 27.228 15.5551 27.25C15.3865 27.272 15.2251 27.2867 15.0711 27.294C14.9171 27.294 14.7778 27.294 14.6531 27.294H13.8391V30H12.0241V22.157H14.6531C15.2251 22.157 15.6945 22.212 16.0611 22.322C16.4351 22.4247 16.7505 22.5823 17.0071 22.795ZM15.5771 25.545C15.8045 25.3837 15.9181 25.1123 15.9181 24.731C15.9181 24.5257 15.8851 24.357 15.8191 24.225C15.7605 24.0857 15.6761 23.9757 15.5661 23.895C15.4121 23.7923 15.2251 23.73 15.0051 23.708C14.7925 23.686 14.5908 23.675 14.4001 23.675H13.8391V25.776H14.4001C14.4881 25.776 14.5835 25.776 14.6861 25.776C14.7961 25.7687 14.9025 25.7577 15.0051 25.743C15.1151 25.7283 15.2178 25.7063 15.3131 25.677C15.4158 25.6477 15.5038 25.6037 15.5771 25.545ZM19.2558 30V22.157H21.7418C22.4018 22.157 22.9554 22.2193 23.4028 22.344C23.8574 22.4613 24.2498 22.6373 24.5798 22.872C25.0491 23.2093 25.3974 23.653 25.6248 24.203C25.8594 24.7457 25.9768 25.3727 25.9768 26.084C25.9768 26.7953 25.8594 27.4223 25.6248 27.965C25.3974 28.5077 25.0491 28.9477 24.5798 29.285C24.2498 29.5197 23.8574 29.6993 23.4028 29.824C22.9554 29.9413 22.4018 30 21.7418 30H19.2558ZM21.0708 28.416H21.7308C22.0681 28.416 22.3651 28.3793 22.6218 28.306C22.8858 28.2327 23.1131 28.13 23.3038 27.998C23.5898 27.8073 23.8024 27.5507 23.9418 27.228C24.0884 26.898 24.1618 26.5167 24.1618 26.084C24.1618 25.644 24.0884 25.2627 23.9418 24.94C23.8024 24.61 23.5898 24.3497 23.3038 24.159C22.9078 23.8877 22.3834 23.752 21.7308 23.752H21.0708V28.416ZM32.3891 23.752H29.4411V25.292H31.9821V26.865H29.4411V30H27.6261V22.157H32.3891V23.752Z"
                            fill="var(--primary-color)"
                          />
                        </svg> */}
                          {getFileIcon(val?.magic, val?.path)}
                        </span>

                        <div>
                          <div className="text-blackText font-cerebriregular text-[14px] capitalize w-[110px] whitespace-nowrap overflow-hidden text-ellipsis">
                            {val.name}
                          </div>
                        </div>
                      </div>

                      <div className="">
                        <img
                          src={dots}
                          alt="dots"
                          className="min-w-[16px]"
                          onClick={(e) => handleFileDelete(val?.guid, e)}
                        />
                        <div className="absolute">
                          {deleteChat1 && deleteChatId1 === val?.guid && (
                            <div
                              id="close"
                              className="relative bg-white border rounded-md shadow-md text-center right-14"
                              onClick={(e) => handleFileChatDelete(val?.guid, e)}
                            >
                              <button
                                id="close1"
                                className="text-[#5A636C] text-[13px] font-cerebri leading-[30px] px-4 py-[2px] mt-1 cursor-pointer"
                              >
                                Delete
                              </button>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* <div className="absolute">
                        {deleteChat1 && deleteChatId1 === val?.guid && (
                          <div
                            // ref={modalRef}
                            id="close"
                            className="relative bg-white border rounded-md shadow-md text-center right-14"
                            onClick={(e) =>
                              handleFileChatDelete(val?.guid, index, e)
                            }
                          >
                            <button
                              id="close1"
                              className="text-[#5A636C] text-[13px] font-cerebri leading-[30px] px-4 py-[2px] mt-1 cursor-pointer"
                            >
                              Delete
                            </button>
                          </div>
                        )}
                      </div> */}
                    </div>
                  );
                })}
              </div>
            )}

            {activeTab === 2 && (
              <div className="sidebar">
                <div className="font-cerebri w-[-webkit-fill-available] flex flex-col justify-between">
                  <div>
                    <h1 className="text-[21px] font-cerebri text-[#495057] leading-[27px] mt-5 mx-5">
                      Chat
                    </h1>
                    {/* <div className="text-center">
                      <button
                        onClick={() => {
                          listData?.setChatHistory(false);
                          listData?.setChatGuid("");
                          navigate("/chat");
                        }}
                        className="bg-customBgDark text-[#fff] rounded-md px-24 pb-2 pt-3 text-[15px] font-cerebriregular xxl:px-10"
                      >
                        New Chat
                      </button>
                    </div> */}
                    {/* <div className="h-[calc(100vh-247px)] overflow-auto scrollbar"> */}
                    <div className="mt-3 h-[calc(100vh-461px)] 1xl:h-[calc(100vh-488px)] overflow-auto scrollbar">
                      <div className="border-t-[0.5px] border-[#F6F6F9]">
                        {renderChatItems()}
                      </div>
                    </div>
                    {/* </div> */}
                  </div>
                  {/* <div className="mx-5 pt-3 pb-3">
                    <h1 className="text-[18px] leading-[25.4px] font-cerebri text-[#495057]">
                      {user?.name}
                    </h1>
                  </div> */}
                </div>
              </div>
            )}
          </div>

          <div className="h-[160px]">
            <div className={`flex items-center gap-2 cursor-pointer px-5 pt-5`}>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: "none" }}
                onChange={handleFileChange}
              />
              <div
                onClick={uploadFile}
                className="flex items-center gap-2 cursor-pointer"
              >
                <span className="bg-customBg p-2 rounded-[5px]">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M21.67 14.3L21.27 19.3C21.12 20.83 21 22 18.29 22H5.71001C3.00001 22 2.88001 20.83 2.73001 19.3L2.33001 14.3C2.25001 13.47 2.51001 12.7 2.98001 12.11C2.99001 12.1 2.99001 12.1 3.00001 12.09C3.55001 11.42 4.38001 11 5.31001 11H18.69C19.62 11 20.44 11.42 20.98 12.07C20.99 12.08 21 12.09 21 12.1C21.49 12.69 21.76 13.46 21.67 14.3Z"
                      stroke="var(--primary-color)"
                      stroke-width="1.5"
                      stroke-miterlimit="10"
                    />
                    <path
                      d="M3.5 11.43V6.28C3.5 2.88 4.35 2.03 7.75 2.03H9.02C10.29 2.03 10.58 2.41 11.06 3.05L12.33 4.75C12.65 5.17 12.84 5.43 13.69 5.43H16.24C19.64 5.43 20.49 6.28 20.49 9.68V11.47"
                      stroke="var(--primary-color)"
                      stroke-width="1.5"
                      stroke-miterlimit="10"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M9.43005 17H14.5701"
                      stroke="var(--primary-color)"
                      stroke-width="1.5"
                      stroke-miterlimit="10"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>

                <div>
                  <div className="text-blackText font-medium font-cerebriregular text-[16px] w-[110px] whitespace-nowrap overflow-hidden text-ellipsis 1xl:text-[14px]">
                    Upload File
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-center items-center gap-2 px-5 mb-2">
              <div class="flex-1 h-[1px] bg-[#CFDFE2]"></div>
              <div className="flex items-center justify-center mb-1 text-blackText font-medium font-cerebri">
                or
              </div>
              <div class="flex-1 h-[1px] bg-[#CFDFE2]"></div>
            </div>

            <div
              className={`flex items-center gap-2 cursor-pointer mb-3 px-2 bg-customBg mx-5 rounded-[8px] py-3 1xl:mb-1 text-blackText font-medium font-cerebriregular border-dashed border-2 border-[#BAD1FF] text-[14px]`}
            >
              <div className="bg-white p-2 rounded-[10px]">
                {/* <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    d="M9.31982 6.49994L11.8798 3.93994L14.4398 6.49994"
                    stroke="#316FF6"
                    stroke-width="1.5"
                    stroke-miterlimit="10"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M11.8799 14.18V4.01001"
                    stroke="#316FF6"
                    stroke-width="1.5"
                    stroke-miterlimit="10"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M4 12C4 16.42 7 20 12 20C17 20 20 16.42 20 12"
                    stroke="#316FF6"
                    stroke-width="1.5"
                    stroke-miterlimit="10"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg> */}
                <AiOutlineCloudUpload className="text-[24px] text-customColor" />
              </div>
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
              >
                {fileName ? (
                  <>
                    {" "}
                    {fileName}{" "}
                    <IoIosClose
                      onClick={setFileName("")}
                      className="cursor-pointer"
                    />{" "}
                  </>
                ) : (
                  <p>
                    Drag & Drop or{" "}
                    <span className="text-customColor"> Browse files </span>
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* <div className="h-[140px]">
            <div
              className={`flex items-center gap-2 cursor-pointer mb-3 px-2 bg-customBg mx-5 rounded-[8px] py-2 1xl:mb-1 text-blackText font-medium font-cerebriregular border-dashed border-2 border-[#BAD1FF] text-[14px]`}
            >
              <div className="bg-white p-2 rounded-[10px]">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    d="M9.31982 6.49994L11.8798 3.93994L14.4398 6.49994"
                    stroke="#316FF6"
                    stroke-width="1.5"
                    stroke-miterlimit="10"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M11.8799 14.18V4.01001"
                    stroke="#316FF6"
                    stroke-width="1.5"
                    stroke-miterlimit="10"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M4 12C4 16.42 7 20 12 20C17 20 20 16.42 20 12"
                    stroke="#316FF6"
                    stroke-width="1.5"
                    stroke-miterlimit="10"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
              >
                {fileName ? (
                  <>
                    {" "}
                    {fileName}{" "}
                    <IoIosClose
                      onClick={setFileName("")}
                      className="cursor-pointer"
                    />{" "}
                  </>
                ) : (
                  <p>
                    Drag & Drop or{" "}
                    <span className="text-customColor"> Browse files </span>
                  </p>
                )}
              </div>
            </div>
            <div className="flex justify-center items-center gap-2 px-5">
              <div class="flex-1 h-[1px] bg-[#CFDFE2]"></div>
              <div className="flex items-center justify-center mb-1 text-blackText font-medium font-cerebri">
                or
              </div>
              <div class="flex-1 h-[1px] bg-[#CFDFE2]"></div>
            </div>
            <div className={`flex items-center gap-2 cursor-pointer mb-3 px-5`}>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: "none" }}
                onChange={handleFileChange}
              />
              <div
                onClick={uploadFile}
                className="flex items-center gap-2 cursor-pointer"
              >
                <span className="bg-customBg p-2 rounded-[5px]">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M21.67 14.3L21.27 19.3C21.12 20.83 21 22 18.29 22H5.71001C3.00001 22 2.88001 20.83 2.73001 19.3L2.33001 14.3C2.25001 13.47 2.51001 12.7 2.98001 12.11C2.99001 12.1 2.99001 12.1 3.00001 12.09C3.55001 11.42 4.38001 11 5.31001 11H18.69C19.62 11 20.44 11.42 20.98 12.07C20.99 12.08 21 12.09 21 12.1C21.49 12.69 21.76 13.46 21.67 14.3Z"
                      stroke="var(--primary-color)"
                      stroke-width="1.5"
                      stroke-miterlimit="10"
                    />
                    <path
                      d="M3.5 11.43V6.28C3.5 2.88 4.35 2.03 7.75 2.03H9.02C10.29 2.03 10.58 2.41 11.06 3.05L12.33 4.75C12.65 5.17 12.84 5.43 13.69 5.43H16.24C19.64 5.43 20.49 6.28 20.49 9.68V11.47"
                      stroke="var(--primary-color)"
                      stroke-width="1.5"
                      stroke-miterlimit="10"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M9.43005 17H14.5701"
                      stroke="var(--primary-color)"
                      stroke-width="1.5"
                      stroke-miterlimit="10"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>

                <div>
                  <div className="text-blackText font-medium font-cerebriregular text-[16px] w-[110px] whitespace-nowrap overflow-hidden text-ellipsis 1xl:text-[14px]">
                    Upload File
                  </div>
                </div>
              </div>
            </div>
          </div> */}

          <h1 className="text-[18px] leading-[25.4px] font-cerebri text-[#495057] ms-5 mt-3">
            {user?.name}
          </h1>
        </>
      )}

      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={style}>
          <div className="font-cerebri text-[20px] text-[#3C3C3C] mb-5 px-[32px] pt-[32px]">
            Add Collection
          </div>
          <hr />
          <div className="px-[32px] pb-[32px]">
            <div>
              <h1 className="text-[#000000] text-[16px] font-cerebriregular leading-[24px] mb-1 mt-5">
                Collection
              </h1>
              <input
                type="text"
                placeholder="Add collection name..."
                className="bg-customBg rounded-lg w-[604px] py-4 px-5 mb-4 font-cerebriregular border-none outline-none text-[#797C8C]"
                value={collection}
                onChange={(e) => setCollection(e.target.value)}
              />
            </div>
            <div>
              <h1 className="text-[#000000] text-[16px] font-cerebriregular leading-[24px] mb-1 mt-1">
                Description
              </h1>
              <input
                type="text"
                placeholder="Add description..."
                className="bg-customBg rounded-lg w-full py-4 px-5 mb-4 font-cerebriregular border-none outline-none text-[#797C8C]"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="flex items-center justify-end mt-4 gap-3">
              <button
                className="text-[18px] font-cerebriregular text-[#3C3C3C] border border-customBorder rounded-lg py-2 px-5 shadow-drop cursor-pointer"
                onClick={handleClose}
              >
                Cancel
              </button>

              <button
                className="text-[18px] font-cerebriregular text-[#FFFFFF] bg-customBgDark rounded-lg py-2 px-7 cursor-pointer"
                onClick={handleAddCollections}
              >
                Add
              </button>
            </div>
          </div>
        </Box>
      </Modal>

      <div className="mx-5 mb-3">
        {/* <div>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
          <div
            className="flex items-center gap-2 border border-customBorderDark py-2 px-5 rounded-lg cursor-pointer"
            onClick={uploadFile}
          >
            <FiDownloadCloud className="text-customColor text-[18px]" />
            <div className="text-customColor font-normal text-[14px] font-cerebri">
              Export saved
            </div>
          </div>
        </div> */}

        {/* <h1 className="text-[18px] leading-[25.4px] font-cerebri text-[#495057]">
          {user?.name}
        </h1> */}
      </div>
    </div>
  );
};

export default ChatBotSideBar;
