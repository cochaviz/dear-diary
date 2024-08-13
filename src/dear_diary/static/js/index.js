window.onload = function () {

  let form = document.getElementById("entry-form");
  // let response_field = document.getElementById("response-field");
  let input_field = document.getElementById("input-field");

  let back_button = document.getElementById("back");
  let question_button = document.getElementById("question");
  let search_button = document.getElementById("search");
  // let submit_button = document.getElementById("submit");

  back_button.addEventListener("pointerup", function () { change_to_tab("entry", entry_tab_settings, post_entry) });
  question_button.addEventListener("pointerup", function () { change_to_tab("question", question_tab_settings, post_question) });
  search_button.addEventListener("pointerup", function () { change_to_tab("search", search_tab_settings, post_search) });

  // make sure content is saved when switching tabs
  let content = {}
  let placeholder = {
    "entry": input_field.placeholder || "What's on your mind?",
    "question": "How did my sentiment change over the last week?",
    "search": "Two weeks ago",
  }

  // when the class changes, we have to save the content and placeholder
  new ClassWatcher(form, on_tab_switch);

  function on_tab_switch(old_name, new_name) {
    // save content and placeholder
    content[old_name] = input_field.value;
    input_field.value = content[new_name] || "";

    placeholder[old_name] = input_field.placeholder;
    input_field.placeholder = placeholder[new_name] || "";
  }

  // TODO Implement
  function post_question() {
    console.log("post_question");
  }
  function post_search() {
    console.log("post_search");
  }

  function post_entry() {
    // send post request to server
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
        show_alert(data.message, "success");
      })
      .catch((error) => {
        console.error("Error:", error);
        show_alert(error, "error");
      });
  }

  function get_content() {
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
        input_field.value = data.content;

        if (data.content) {
          on_has_content();
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        show_alert(error, "error");
      });
  }

  function on_has_content() {
    question_button.disabled = false;
    search_button.disabled = false;
  }

  function change_to_tab(name, tab_function, submit_callback) {
    tab_function();
    form.classList = [name];

    // all the benefits of a form without the page refresh!
    form.onsubmit = function (_) {
      submit_callback();
      return false;
    } 
  }

  function entry_tab_settings() {
    search_button.disabled = false;
    question_button.disabled = false;
    back_button.disabled = true;
  }

  function question_tab_settings() {
    question_button.disabled = true;
    search_button.disabled = false;
    back_button.disabled = false;
  }

  function search_tab_settings() {
    search_button.disabled = true;
    question_button.disabled = false;
    back_button.disabled = false;
  }

  function show_alert(message, type) {
    let alert_box = document.getElementById("alert-box");
    let alert_message = document.getElementById("alert-message");

    alert_box.classList = [type];
    alert_message.innerHTML = message;
  }

  // entry tab is default
  change_to_tab("entry", entry_tab_settings, post_entry)();
  get_content(date);
};


class ClassWatcher {

    constructor(targetNode, classSwitchedCallback) {
        this.targetNode = targetNode
        this.classSwitchedCallback = classSwitchedCallback
        this.observer = null
        console.log(targetNode)
        this.lastClassState = targetNode.classList[0]

        this.init()
    }

    init() {
        this.observer = new MutationObserver(this.mutationCallback)
        this.observe()
    }

    observe() {
        this.observer.observe(this.targetNode, { attributes: true })
    }

    disconnect() {
        this.observer.disconnect()
    }

    mutationCallback = mutationsList => {
        for(let mutation of mutationsList) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                let currentClassState = mutation.target.classList[0]
                if(this.lastClassState !== currentClassState) {
                    this.classSwitchedCallback(this.lastClassState, currentClassState)
                    this.lastClassState = currentClassState
                }
            }
        }
    }
}
