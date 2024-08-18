window.onload = function () {
  let form = document.getElementById("entry-form");
  let response_field = document.getElementById("response-field");
  let input_field = document.getElementById("input-field");

  let back_button = document.getElementById("back");
  let question_button = document.getElementById("question");
  let search_button = document.getElementById("search");
  let submit_button = document.getElementById("submit");
  let dark_mode_button = document.getElementById("dark-mode");

  let alert_box = document.getElementById("alert-box");
  let alert_message = document.getElementById("alert-message");

  let remote_content = "";
  let is_submitting = false;
  let is_dirty = false;

  // make sure content is saved when switching tabs
  let content = {}
  let response = {}

  let placeholder = {
    "entry": input_field.placeholder || "What's on your mind?",
    "question": "How did my sentiment change over the last week?",
    "search": "Two weeks ago",
  }

  back_button.addEventListener("pointerup",  () => { change_to_tab("entry", entry_tab_settings) });
  question_button.addEventListener("pointerup",  () => { change_to_tab("question", question_tab_settings) });
  search_button.addEventListener("pointerup",  () => { change_to_tab("search", search_tab_settings) });
  dark_mode_button.addEventListener("pointerup", toggle_color_scheme);

  submit_button.addEventListener("pointerup", () => {
    is_submitting = true;

    if (form.classList[0] == "entry") {
      post_entry();
    } else if (form.classList[0] == "question") {
      post_question();
    } else if (form.classList[0] == "search") {
      search();
    }
    is_submitting = false;
  });

  alert_box.addEventListener("pointerup", () => {
    // has to be like this because otherwise it fucks up
    // alert_box.style.opacity = 0;
    alert_box.classList = [];
  });

  // TODO Implement
  function post_question() {
    console.log("post_question");
  }

  function search() {
    let query = input_field.value;

    fetch(`/entry?query=${query}`)
      .then((response) => {
        if (!response.ok) {
          if (response.status == 400) {
            throw new Error("Invalid query format, please try something else");
          } else if (response.status == 422) {
            throw new Error("Please provide a query");
          }
          throw new Error(`HTTP error: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        createDateLinksList(
          data.map(entry => entry.date), response_field
        );
      })
      .catch((error) => {
        console.error("Error:", error);
        show_alert(error, "error");
      });
  }

  function post_entry() {
    fetch(`/entry`, {
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
        entry_tab_settings();  // enable buttons
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

    if (response_field.childNodes.length > 0) {
      response[old_tab] = Array
          .from(response_field.childNodes)
          .map(node => node.cloneNode(true));
    }
    response_field.replaceChildren();

    if(response[new_tab]) {
      console.log(response[new_tab]);
      response[new_tab].forEach((child) => {
        response_field.appendChild(child);
      });
    }

    placeholder[old_tab] = input_field.placeholder;
    input_field.placeholder = placeholder[new_tab] || "";

    // after content has been set, we can enable the buttons
    // since some depend on the content (input_field.value)
    tab_settings();
  }

  window.addEventListener("beforeunload", unsaved_changes_handler);

  input_field.addEventListener("input", () => {
    if (form.classList[0] == "entry" ) {
      is_dirty = input_field.value !== remote_content;
    }
  });

  const entry_tab_settings = () => {
    console.log(remote_content.length);
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

  function set_color_scheme_light() {
    document.body.classList = ["light"];
    dark_mode_button.classList = ["set-dark"]
  }

  function set_color_scheme_dark() {
    document.body.classList = ["dark"];
    dark_mode_button.classList = ["set-light"]
  }

  function toggle_color_scheme() {
    if (document.body.classList[0] == "dark") {
      set_color_scheme_light();
    } else {
      set_color_scheme_dark();
    }
  }

  // default page behavior
  get_content(date);

  if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    set_color_scheme_dark();
  } else {
    set_color_scheme_light();
  }
};

function createDateLinksList(dates, parentElement) {
    if (parentElement.children.length > 0) {
        parentElement.replaceChildren();
    }
    const ul = document.createElement('ul');
    
    dates.forEach(dateString => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        
        a.href = `/?date=${encodeURIComponent(dateString)}`;
        a.textContent = dateString;

        li.appendChild(a);
        ul.appendChild(li);
    });
    parentElement.appendChild(ul);
}