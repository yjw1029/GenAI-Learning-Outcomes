function setupTrigers() {
  function setStartTimeText() {
    try {
      const start_time = document.getElementById("start_time").value;
      const current_time = new Date().getTime() / 1000;
      const diff = current_time - start_time;
      const diff_min = Math.floor(diff / 60);
      const diff_sec = Math.floor(diff % 60);
      const diff_text = diff_min + " min " + diff_sec + " sec";
      document.getElementById("start_time_text").innerHTML =
        "(Started " + diff_text + ")";
    } catch (e) {
      // console.log(e);
    }
  }

  setStartTimeText();
  window.setInterval(setStartTimeText, 1000);

  function setCurrentStageStartTimeText() {
    try {
      const start_time = document.getElementById(
        "current_stage_start_time"
      ).value;
      const end_time = document.getElementById("current_stage_end_time").value;
      const current_time = new Date().getTime() / 1000;
      const diff = current_time - start_time;
      const diff_min = Math.floor(diff / 60);
      const diff_sec = Math.floor(diff % 60);
      const diff_text = diff_min + " min " + diff_sec + " sec";
      document.getElementById("current_stage_start_time_text").innerHTML =
        "(This stage started " + diff_text + ")";

      if (end_time > 0) {
        const diff = end_time - current_time;
        if (diff <= 0) {
          document.getElementById("current_stage_start_time_text").innerHTML =
            "(This stage ended, please start the next stage soon)";

          document.title = "llm4edu - Stage Ended";
        } else {
          const diff_min = Math.floor(diff / 60);
          const diff_sec = Math.floor(diff % 60);
          const diff_text = diff_min + " min " + diff_sec + " sec";
          const diff_text_short = diff_min + ":" + diff_sec;
          document.getElementById("current_stage_start_time_text").innerHTML +=
            "(Time left in this stage " + diff_text + ")";

          // title
          document.title = "llm4edu - " + diff_text_short;
        }
      }
    } catch (e) {
      // console.log(e);
    }
  }

  function notifyReminingTimeOnce(reminingTime) {
    // notify once for each remining time
    const reminingTimeM = Math.floor(reminingTime / 60);
    const reminderKey = "reminder_" + reminingTimeM;
    const reminder = sessionStorage.getItem(reminderKey);
    if (reminder) {
      return;
    }
    sessionStorage.setItem(reminderKey, true);
    alert("About " + reminingTimeM + " minutes left. Please finish this stage soon.");
    console.log("About " + reminingTimeM + " minutes left. Please finish this stage soon.");
  }

  function checkReminingTime() {
    try {
      const end_time = document.getElementById("current_stage_end_time").value;
      const current_time = new Date().getTime() / 1000;
      const diff = end_time - current_time;
      if (diff > 0 && diff < 70) {
        notifyReminingTimeOnce(diff);
      } else {
        if (diff <= 0) {
          if (window.location.href.indexOf("home") > -1) {
            alert("This stage has ended. Please start the next stage soon.");
            window.location.href = "/progress";
          }
        }
      }
    } catch (e) {
      console.log(e);
    }
  }

  setCurrentStageStartTimeText();
  sessionStorage.clear();
  window.setInterval(setCurrentStageStartTimeText, 1000);
  window.setInterval(checkReminingTime, 1000);

  // TODO: check if user is not logged in, then redirect to login page
}
