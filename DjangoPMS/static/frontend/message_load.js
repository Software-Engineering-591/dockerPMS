let submit = document.getElementById("submit");

// Go to Last Message
window.addEventListener("load", function () {
  var msgBox = document.getElementById("msgBox");
  msgBox.scrollTop = msgBox.scrollHeight;
  submit.scrollIntoView({ behavior: "smooth", block: "end" });
});

// CTRL ENTER KEYSTROKE
document
  .getElementById("msgTextArea")
  .addEventListener("keydown", function (event) {
    if (event.ctrlKey && event.key === "Enter") {
      event.preventDefault(); // Prevent inserting a newline
      submit.click();
    }
  });
