"use client";
import { useState } from "react";

export default function Home() {

  const [response, setResponse] = useState("")

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      // Handle sending the message
      const message = e.currentTarget.value;
      console.log("Message sent:", message);
      if (message != "") {


        e.currentTarget.value = ""; // Clear the input after sending

        console.log("Sending message to backend:", `${process.env.NEXT_PUBLIC_BACKENDURL}/chat`);
        fetch(`${process.env.NEXT_PUBLIC_BACKENDURL}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question: message }),
        })
          .then((response) => response.json())
          .then((data) => {
            console.log("Response from backend:", data.response);
            // You can update the UI with the response here
            setResponse(data.response)
          })
          .catch((error) => {
            console.error("Error sending message:", error);
          });
      } else {
        alert("Please ask your question")
      }
    }
  };

  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">


        <div className="vh-100 w-full">
          <div className="vh-80 overflow-y-auto mb-4">

            <div>
              {response}
            </div>

          </div>
          <div className="vh-20 flex items-center justify-center   position-absolute bottom-0 left-0 right-0 p-4 bg-white dark:bg-black">
            <input className="border border-gray-300 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
              type="text" placeholder="Type your message..."
              onKeyDown={handleKeyDown}
            />

          </div>
        </div>

      </main>
    </div>
  );
}
