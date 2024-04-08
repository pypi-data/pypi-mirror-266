import React, { useState, useEffect, useContext, memo } from "react";
import roleContext from "../../contexts/roleContext";
import { API_Path } from "../../API/ApiComment";
import MarkdownRenderer from "react-markdown-renderer";

const EnhancedPrompt = ({
  prompt,
  guid,
  setNewDetails,
  setSend,
  apiActive,
}) => {
  const user = JSON.parse(localStorage.getItem("komodoUser"));
  const chatContext = useContext(roleContext);
  const [fullMessage, setFullMessage] = useState("");

  useEffect(() => {
    if (prompt !== "" && apiActive) {
      setFullMessage("");
      let eventSource;
      if (!["", undefined]?.includes(guid)) {
        eventSource = new EventSource(
          `${API_Path.agentAskStreamedBaseUrl}?email=${user?.email}&agent_shortcode=${chatContext?.reactSelect?.shortcode}&prompt=${prompt}&guid=${guid}`
        );
      } else {
        eventSource = new EventSource(
          `${API_Path.agentAskStreamedBaseUrl}?email=${user?.email}&agent_shortcode=${chatContext?.reactSelect?.shortcode}&prompt=${prompt}`
        );
      }

      eventSource.onmessage = (event) => {
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
        console.log(" :>> ", ["", undefined]?.includes(guid));
        if (["", undefined]?.includes(guid)) {
          chatContext?.conversations(true);
        }
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
      <MarkdownRenderer
        markdown={fullMessage}
        className="font-cerebriregular text-[15px] text-justify removemargin"
      />
    </div>
  );
};

export default memo(EnhancedPrompt);
