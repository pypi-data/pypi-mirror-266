var firstRun = true;


function main() {
    const editor = initEditor();
    addEventListeners(editor);

    window.addEventListener("error", (error) => {
        const display = document.getElementById("runtime-error-display");
        const escaped = new Option(error.message).innerHTML;
        display.innerHTML = escaped;
        display.style.display = "block";
    });

    showLoaded(true, () => {});
}


function initEditor() {
    const editor = ace.edit("editor");
    editor.getSession().setMode("ace/mode/python");
    return editor;
}


function runProgram(editor) {
    showLoading();

    const rawCode = editor.getValue();

    const wrappedCode = "<py-script id='code-tag'>\n" + rawCode + "\n</py-script>";
    document.getElementById("main-script").innerHTML = wrappedCode;

    document.querySelectorAll(".py-error").forEach((x) => x.remove());
    document.getElementById("runtime-error-display").style.display = "none";

    setTimeout(() => {
        showLoaded(false, () => document.getElementById("canvas-holder").scrollIntoView());
    }, 500);
}


function addEventListeners(editor) {
    document.getElementById("run-button").addEventListener("click", () => runProgram(editor));
}


function showLoading() {
    document.getElementById("loading-msg").style.display = "inline-block";
    document.getElementById("loaded-msg").style.display = "none";
    
    const loadingContent = document.getElementById("sketch-load-message-content");
    loadingContent.innerHTML = "Loading environment...";

    const progressBar = document.getElementById("sketch-load-progress");
    progressBar.style.display = "inline-block";
    progressBar.value = 0;
    const incrementBar = () => {
        progressBar.value += 1;

        if (progressBar.value < 19) {
            setTimeout(incrementBar, 500);
        }
    };
    incrementBar();
}


function showLoaded(forceImmediate, scrollCallback) {
    document.getElementById("loading-msg").style.display = "none";
    document.getElementById("loaded-msg").style.display = "inline-block";
    scrollCallback();
}


main();