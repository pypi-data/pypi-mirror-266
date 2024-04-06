const USE_CASES = [
    "everyone",
    "interactive science",
    "data visualizations",
    "visual art",
    "simulations",
    "UX prototypes",
    "games",
    "lessons",
    "maps"
];

const PLATFORMS = [
    "all platforms",
    "desktop",
    "laptop",
    "web",
    "browser",
    "mobile",
    "server",
    "Jupyter",
    "notebooks"
];

const state = {
    "paused": false,
    "countdownRemaining": 10
};


function transition() {
    const useCase = USE_CASES[Math.floor(Math.random() * USE_CASES.length)];
    const platform = PLATFORMS[Math.floor(Math.random() * PLATFORMS.length)];

    const useCaseElem = document.getElementById("use-case");
    const platformElem = document.getElementById("platform");

    useCaseElem.innerHTML = useCase;
    platformElem.innerHTML = platform;

    const applyAnimation = (elem) => {
        elem.animate(
            [
                { opacity: 0 },
                { opacity: 1 }
            ],
            {
                duration: 1000,
                iterations: 1
            }
        );
    };

    applyAnimation(useCaseElem);
    applyAnimation(platformElem);
}


function countdown() {
    if (state["countdownRemaining"] == 0) {
        transition();
        state["countdownRemaining"] = 5;
        const newText = "Shuffling...";
        document.getElementById("countdown").innerHTML = newText;
    } else {
        const countdownRemaining = state["countdownRemaining"];
        const newText = "Shuffling in " + countdownRemaining + " seconds...";
        document.getElementById("countdown").innerHTML = newText;

        if (!state["paused"]) {
            state["countdownRemaining"] = countdownRemaining - 1;
        }
    }

    setTimeout(countdown, 1000);
}


function setupControls() {
    const pauseLink = document.getElementById("pause-link");
    pauseLink.addEventListener("click", (event) => {
        state["paused"] = !state["paused"];

        const newMessage = state["paused"] ? "Resume" : "Pause";
        pauseLink.innerHTML = newMessage;

        event.preventDefault();
    });

    const shuffleLink = document.getElementById("shuffle-link");
    shuffleLink.addEventListener("click", (event) => {
        transition();

        state["countdownRemaining"] = 5;

        event.preventDefault();
    });
}


setupControls();
countdown();
