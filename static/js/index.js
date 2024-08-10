window.onload = function () {
  // get dashboard and collapse it
  let dashboard = document.getElementById("dashboard");
  let dashboard_default_classes = ["side-bar"];

  let question_button = document.getElementById("question");
  let question_open_icon = document.getElementById("question-open-icon");
  let question_close_icon = document.getElementById("question-close-icon");
  let question_submit_button = document.getElementById("question-submit");
  let submit_button = document.getElementById("submit");
  let search_button = document.getElementById("search");

  submit_button.addEventListener("click", submit_entry);

  // FIXME: Now done server-side
  // function current_date() {
  //   let today = new Date();
  //   let dd = String(today.getDate()).padStart(2, "0");
  //   let mm = String(today.getMonth() + 1).padStart(2, "0"); //January is 0!
  //   let yyyy = today.getFullYear();
  //   return `${yyyy}-${mm}-${dd}`;
  // }

  function submit_entry() {
    let diary_entry = document.getElementById("diary-field").value;
    set_entry_remote(date, diary_entry);
  }

  function set_entry_remote(date, entry) {
    // send post request to server
    fetch(`/entry/`, {
      method: "POST",
      body: JSON.stringify({
        date: date,
        content: entry,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          if (response.status == 400) {
            throw new Error("Please enter a diary entry");
          }
          throw new Error(`HTTP error: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log(data);
        show_alert(data.message, "success");
        on_submit_success();
      })
      .catch((error) => {
        console.error("Error:", error);
        show_alert(error, "error");
      });
  }

  function get_entry_remote(date) {
    return fetch(`/entry/${date}`)
      .then((response) => {
        if (!response.ok) {
          if (response.status == 404) {
            return { content: "" };
          }
          throw new Error(`HTTP error: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log(data);
        document.getElementById("diary-field").value = data.content;

        // if entry is not empty, expand the dashboard
        if (data.content) {
          on_submit_success();
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        show_alert(error, "error");
      });
  }

  function on_submit_success() {
    question_button.disabled = false;
    search_button.disabled = false;
    question_button.addEventListener("click", dashboard_expand_stage_one);
    question_submit_button.addEventListener(
      "click",
      dashboard_expand_stage_two
    );
  }

  function dashboard_expand_stage_one() {
    // set classes
    dashboard.classList = [];
    dashboard.classList.add("expand-stage-one");
    dashboard_default_classes.forEach((element) => {
      dashboard.classList.add(element);
    });
    // make sure we can collapse it
    question_button.addEventListener("click", dashboard_collapse);
    question_button.removeEventListener("click", dashboard_expand_stage_one);
    // change icon
    question_open_icon.style.display = "none";
    question_close_icon.style.display = "block";
  }

  function dashboard_expand_stage_two() {
    dashboard.classList = [];
    dashboard.classList.add("expand-stage-two");
    dashboard_default_classes.forEach((element) => {
      dashboard.classList.add(element);
    });
  }

  function dashboard_collapse() {
    // reset classes
    dashboard.classList = [];
    dashboard.classList.add("collapsed");
    dashboard_default_classes.forEach((element) => {
      dashboard.classList.add(element);
    });
    // make sure we can expand it
    question_button.addEventListener("click", dashboard_expand_stage_one);
    question_button.removeEventListener("click", dashboard_collapse);
    // change icon
    question_open_icon.style.display = "block";
    question_close_icon.style.display = "none";
  }

  function show_alert(message, type) {
    let alert_box = document.getElementById("alert-box");
    let alert_message = document.getElementById("alert-message");

    alert_box.classList = [type];
    alert_message.innerHTML = message;
  }

  // check whether we have an entry for today and display it
  get_entry_remote(date);
};
