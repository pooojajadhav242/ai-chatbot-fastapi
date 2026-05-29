async function askAI() {
    const chatBox =
        document.getElementById(
            "chat-box"
        )
    try {

        const username =
            document.getElementById(
                "username"
            ).value

        const question =
            document.getElementById(
                "question"
            ).value

        

        // User message
        chatBox.innerHTML += `

        <div class="message user">
            ${question}
        </div>
        `

        // Loader
        chatBox.innerHTML += `

       <div class="typing">
        <span></span>
        <span></span>
        <span></span>
        </div>
        `

        chatBox.scrollTop =
            chatBox.scrollHeight

        const response =
            await fetch(

            "http://127.0.0.1:8000/ask-ai",

            {
                method: "POST",

                headers: {
                    "Content-Type":
                    "application/json"
                },

                body: JSON.stringify({

                    username: username,

                    question: question
                })
            }
        )

        const data =
                await response.json()

            if (!response.ok) {

                throw new Error(
                    data.detail
                )
            }

        // Remove loader
        const loader =
            document.querySelector(
                ".loading"
            )

        if (loader) {

            loader.remove()
        }

        // AI response
        chatBox.innerHTML += `

        <div class="message ai">
            ${marked.parse(data.answer)}
        </div>
        `

        chatBox.scrollTop =
            chatBox.scrollHeight

        document.getElementById(
            "question"
        ).value = ""
    }

    catch(error) {

        const loader =
        document.querySelector(
            ".loading"
        )
    
    if (loader) {
    
        loader.remove()
    }
    
    chatBox.innerHTML += `
    
    <div class="message ai error">
    
        ${error.message}
    
    </div>
    `
    }
}

document
    .getElementById(
        "question"
    )

    .addEventListener(

        "keypress",

        function(event) {

            if (
                event.key === "Enter"
            ) {

                askAI()
            }
        }
    )