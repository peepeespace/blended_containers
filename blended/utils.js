const SLEEP = (ms) => {
    return new Promise((resolve) => setTimeout(resolve, ms));
};

const getSleepTime = () => {
    let sleepTime = Math.floor(Math.random() * 10) * 1000;
    if (sleepTime == 0) {
        sleepTime = 1000;
    } else if (sleepTime >= 4000) {
        sleepTime = 2000;
    }
    return sleepTime;
};

module.exports = {
    SLEEP,
    getSleepTime
};