window.onload = function () {
  let form = document.getElementById("entry-form");
  let response_field = document.getElementById("response-field");
  let input_field = document.getElementById("input-field");

  let back_button = document.getElementById("back");
  let question_button = document.getElementById("question");
  let search_button = document.getElementById("search");
  let submit_button = document.getElementById("submit");

  let alert_box = document.getElementById("alert-box");
  let alert_message = document.getElementById("alert-message");

  let remote_content = "";
  let is_submitting = false;
  let is_dirty = false;

  // make sure content is saved when switching tabs
  let content = {}
  let placeholder = {
    "entry": input_field.placeholder || "What's on your mind?",
    "question": "How did my sentiment change over the last week?",
    "search": "Two weeks ago",
  }

  back_button.addEventListener("pointerup",  () => { change_to_tab("entry", entry_tab_settings) });
  question_button.addEventListener("pointerup",  () => { change_to_tab("question", question_tab_settings) });
  search_button.addEventListener("pointerup",  () => { change_to_tab("search", search_tab_settings) });

  submit_button.addEventListener("pointerup", () => {
    is_submitting = true;

    if (form.classList[0] == "entry") {
      post_entry();
    } else if (form.classList[0] == "question") {
      post_question();
    } else if (form.classList[0] == "search") {
      post_search();
    }
    is_submitting = false;
  });

  // TODO Implement
  function post_question() {
    console.log("post_question");
  }
  function post_search() {
    console.log("post_search");
  }

  function post_entry() {
    fetch(`/entry/`, {
      method: "POST",
      body: JSON.stringify({
        date: date,
        content: input_field.value,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          if (response.status == 422) {
            throw new Error("Please enter a diary entry");
          }
          throw new Error(`HTTP error: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log(data);
        set_entry_content(input_field.value);
        show_alert(data.message, "success");
      })
      .catch((error) => {
        console.error("Error:", error);
        show_alert(error, "error");
      });
  }

  function get_content() {
    fetch(`/entry/${date}`)
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

        if (data.content) {
          set_entry_content(data.content);
          entry_tab_settings();
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        show_alert(error, "error");
      });
  }

  function set_entry_content(value) {
    remote_content = value;
    input_field.value = value;
    is_dirty = false;
  }

  const unsaved_changes_handler = (event) => {
    if (is_dirty && !is_submitting) {
      event.preventDefault();
      event.returnValue = true;
    }
  }

  function change_to_tab(new_tab, tab_settings) {
    old_tab = form.classList[0];
    form.classList = [new_tab];

    content[old_tab] = input_field.value;
    input_field.value = content[new_tab] || "";

    placeholder[old_tab] = input_field.placeholder;
    input_field.placeholder = placeholder[new_tab] || "";

    // after content has been set, we can enable the buttons
    // since some depend on the content (input_field.value)
    tab_settings();

    // testing:
    show_alert(`Switched to ${new_tab}`, "info");
    console.log("Entry tab settings applied, response_field disabled:", response_field.disabled);
  }

  window.addEventListener("beforeunload", unsaved_changes_handler);

  input_field.addEventListener("input", () => {
    if (form.classList[0] == "entry" ) {
      is_dirty = input_field.value !== remote_content;
    }
  });

  const entry_tab_settings = () => {
    question_button.disabled = remote_content.length == 0;
    search_button.disabled = remote_content.length == 0;
    back_button.disabled = true;
    response_field.classList = ["hidden"];
  }

  const question_tab_settings = () => {
    question_button.disabled = true;
    search_button.disabled = false;
    back_button.disabled = false;
    response_field.classList = [];
  }

  const search_tab_settings = () => {
    search_button.disabled = true;
    question_button.disabled = false;
    back_button.disabled = false;
    response_field.classList = [];
  }

  function show_alert(message, type) {
    alert_box.classList = [type];
    alert_message.innerHTML = message;
  }

  get_content(date);
};