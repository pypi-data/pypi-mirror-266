import React, { useState, useEffect, useContext, memo } from "react";
import roleContext from "../../contexts/roleContext";
import { API_Path } from "../../API/ApiComment";
import MarkdownRenderer from "react-markdown-renderer";
import { useLocation } from "react-router";

const EnhancedBot = ({ prompt, guid, setNewDetails, setSend, apiActive }) => {
  const user = JSON.parse(localStorage.getItem("komodoUser"));
  const chatContext = useContext(roleContext);
  const [fullMessage, setFullMessage] = useState("");
  const location = useLocation();
  const pathnameParts = location.pathname.split("/");
  const shortcode = pathnameParts[pathnameParts.length - 1];
  const filesId = location?.state?.fileId;

  console.log("shortcode :>> ", shortcode);
  console.log("filesId :>> ", filesId);
  console.log("locationabcd :>> ", location);
  console.log("context :>> ", chatContext);
  console.log("guid :>> ", guid);

  useEffect(() => {
    if (prompt !== "" && apiActive) {
      setFullMessage("");
      let eventSource;
      // if (!["", undefined]?.includes(guid)) {
      //     eventSource = new EventSource(`${API_Path.streamedApi}email=${user?.email}&agent_shortcode=${chatContext?.reactSelect?.shortcode}&prompt=${prompt}&guid=${guid}`);
      // } else {

      // if (!["", undefined]?.includes(guid)) {
      //   eventSource = new EventSource(
      //     `${API_Path.agentAskStreamedBaseUrl}?email=${user?.email}&agent_shortcode=${chatContext?.reactSelect?.shortcode}&prompt=${prompt}?&collection_shortcode=${shortcode}&file_guid=${filesId}&guid=${guid}`
      //   );
      // } else {
      //   eventSource = new EventSource(
      //     `${API_Path.agentAskStreamedBaseUrl}?email=${user?.email}&agent_shortcode=${chatContext?.reactSelect?.shortcode}&prompt=${prompt}?&collection_shortcode=${shortcode}&file_guid=${filesId}`
      //   );
      // }
      let url = `${API_Path.agentAskStreamedBaseUrl}?email=${user?.email}&agent_shortcode=${chatContext?.reactSelect?.shortcode}&prompt=${prompt}&collection_shortcode=${shortcode}`;

      if (filesId) {
        url += `&file_guid=${filesId}`
      }

      if (!["", undefined]?.includes(guid)) {
        url += `&guid=${guid}`
      }
      eventSource = new EventSource(url);


      // sample.kmdo.app/api/v1/agent/ask-streamed?email=ryan@komodoapp.ai&agent_shortcode=summarizer&prompt=what are the toughest tasks?&collection_shortcode=ada1d01c-2f76-4bad-9f5f-7dbdbaddc426&file_guid=c399733f-a1f9-4d34-930a-17cc2aaa5234

      // }

      // eventSource.onmessage = (event) => {
      //   const newMessage = event.data;
      //   setFullMessage((prvMsg) => prvMsg + " " + newMessage);
      // };
      eventSource.onmessage = (event) => {
        console.log("event :>> ", event);
        const binaryStr = atob(event.data);
        const bytes = new Uint8Array(
          binaryStr.split("").map((char) => char.charCodeAt(0))
        );
        const newMessage = new TextDecoder("utf-8").decode(bytes);
        setFullMessage((prvMsg) => prvMsg + newMessage);
      };

      eventSource.addEventListener("stream-complete", function (e) {
        eventSource.close();
        setSend(false);
        if (["", undefined]?.includes(guid)) {
          chatContext?.conversations(true);
        }
        // chatContext?.conversations();
        // if (["", undefined]?.includes(guid)) {
        //     chatContext?.conversations(true)
        // }
        // else {
        //     chatContext?.conversations()
        // }
      });

      eventSource.onopen = (event) => {
        console.log("Connection to server opened.");
      };

      eventSource.onclose = function () {
        console.log("Connection closed by the server.");
      };

      eventSource.onerror = (event) => {
        if (eventSource.readyState === EventSource.CLOSED) {
          console.error("Connection was closed.");
        } else {
          console.error("An error occurred:", event);
        }
        eventSource.close();
      };
      return () => {
        eventSource.close();
      };
    }
  }, [prompt, apiActive]);

  useEffect(() => {
    if (fullMessage !== "") {
      setNewDetails((perState) => {
        return { ...perState, chatRes: fullMessage };
      });
    }
  }, [fullMessage]);

  return (
    <div className="w-fit text-[#495057]">
      {/* <p
          className="font-cerebriregular text-[15px] leading-[34px]"
          dangerouslySetInnerHTML={{
            __html: fullMessage.replace(/\n/g, "<br>"),
          }}
        ></p> */}
      <MarkdownRenderer
        markdown={fullMessage}
        className="font-cerebriregular text-[15px] px-3 text-blackText removemargin"
      />
    </div>
  );
};

export default memo(EnhancedBot);
