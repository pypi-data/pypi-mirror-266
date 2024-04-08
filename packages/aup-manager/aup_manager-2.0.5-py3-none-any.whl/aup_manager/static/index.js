const Editor = toastui.Editor;

if (document.querySelector("#editor")) {
  var editor = new Editor({
    el: document.querySelector("#editor"),
    height: "500px",
    initialEditType: "markdown",
    previewStyle: "vertical",
  });
}

function stepper_name_continue() {
  let aup_name_form = $("#aupNameForm");
  if (aup_name_form.val() === "") {
    aup_name_form.addClass("is-invalid");
  } else {
    aup_name_form.removeClass("is-invalid");
    toggle_select_name_elements();
  }
}

function stepper_content_continue() {
  let empty_content = $("#empty_content");
  if (editor.getMarkdown() === "") {
    empty_content.removeClass("d-none");
  } else {
    empty_content.addClass("d-none");
    toggle_fill_content_elements();
  }
}

function stepper_content_back() {
  toggle_select_name_elements();
}

function stepper_cond_back() {
  toggle_fill_content_elements();
}

function build_condition_to_save() {
  let conditions = [];
  let outer_index = 1;
  let inner_index = 1;
  while ($("#Condition" + outer_index).length) {
    conditions.push([]);
    while ($("#Condition" + outer_index + "_" + inner_index).length) {
      let condition_ent = $(
        "#Condition" + outer_index + "_" + inner_index + "_text",
      );
      let type_id = condition_ent.attr("type_id");
      let type_name = condition_ent.text().trim();
      let type = type_id.split(":", 1)[0];
      let name = type_name.substring(type.length + 1);
      conditions[outer_index - 1].push({
        name: name,
        type: type,
        type_id: type_id,
      });
      inner_index++;
    }
    inner_index = 1;
    outer_index++;
  }
  return conditions;
}

$("#stepper_finish").click(function () {
  let empty_conditions = $("#empty_conditions");
  if (!$("#Condition1").length) {
    empty_conditions.removeClass("d-none");
  } else {
    let conditions = build_condition_to_save();
    $.ajax({
      url: "/save_aup",
      dataType: "json",
      type: "post",
      contentType: "application/json",
      data: JSON.stringify({
        name: $("#aupNameForm").val(),
        content: editor.getMarkdown(),
        conditions: conditions,
      }),
      processData: false,
      success: function (response) {
        alert("Aup was successfully saved.");
        window.location.href = response["redirect_url"];
      },
      error: function (jqXhr, textStatus, errorThrown) {
        alert("Error occurred");
        console.log(errorThrown);
      },
    });
  }
});

function toggle_select_name_elements() {
  toggle_visibility(document.getElementById("select_name_box"));
  toggle_visibility(document.getElementById("fill_content_box"));
  toggle_primary_to_success(document.getElementById("stepper_but_1"));
  toggle_color_secondary_to_primary(document.getElementById("stepper_but_2"));
  toggle_text_secondary(document.getElementById("sel_name_text"));
  toggle_text_secondary(document.getElementById("fill_cont_text"));
}

function toggle_fill_content_elements() {
  toggle_visibility(document.getElementById("fill_content_box"));
  toggle_visibility(document.getElementById("conditions_box"));
  toggle_primary_to_success(document.getElementById("stepper_but_2"));
  toggle_color_secondary_to_primary(document.getElementById("stepper_but_3"));
  toggle_text_secondary(document.getElementById("fill_cont_text"));
  toggle_text_secondary(document.getElementById("sel_con_text"));
}

function toggle_visibility(element) {
  element.classList.toggle("d-none");
}

function toggle_primary_to_success(element) {
  element.classList.toggle("bg-primary");
  element.classList.toggle("bg-success");
}

function toggle_color_secondary_to_primary(element) {
  element.classList.toggle("bg-secondary");
  element.classList.toggle("bg-primary");
}

function toggle_text_secondary(element) {
  element.classList.toggle("text-secondary");
}

let select_type_element = $("#select_type");
let select_condition_element = $("#select_condition");
let select_entity_element = $("#select_entity");
let add_condition_button = $("#stepper_add_condition");

function add_condition_button_enabler() {
  if (
    $("option:selected", select_condition_element).val() !== "0" &&
    $("option:selected", select_type_element).val() !== "0" &&
    $("option:selected", select_entity_element).val() !== "0"
  ) {
    if (add_condition_button.hasClass("disabled")) {
      add_condition_button.removeClass("disabled");
    }
  } else if (!add_condition_button.hasClass("disabled")) {
    add_condition_button.addClass("disabled");
  }
}

select_type_element.on("change", function () {
  let value = $("option:selected", this).text();
  let select_entity_elem = $("#select_entity");
  if ($("option:selected", this).val() !== "0") {
    select_entity_elem.prop("disabled", false);
  } else {
    select_entity_elem.prop("disabled", true);
    add_condition_button_enabler();
    return;
  }
  let entities_list = entities[value];
  $("#select_entity option:gt(0)").remove();
  for (let i = 0; i < entities_list.length; i++) {
    select_entity_elem.append(
      $("<option></option>")
        .attr("value", i + 1)
        .attr("type_id", entities_list[i].type_id)
        .text(entities_list[i].name),
    );
  }
  add_condition_button_enabler();
});

select_condition_element.on("change", function () {
  add_condition_button_enabler();
});

select_entity_element.on("change", function () {
  add_condition_button_enabler();
});

function select_condition_updater() {
  let index = 1;
  $("#select_condition option:gt(0)").remove();
  while ($("#Condition" + index).length) {
    select_condition_element.append(
      $("<option></option>")
        .attr("value", index + 1)
        .text("Condition" + index),
    );
    index++;
  }
  select_condition_element.append(
    $("<option></option>")
      .attr("value", index + 1)
      .text("Condition" + index),
  );
  add_condition_button_enabler();
}

add_condition_button.click(function () {
  let condition_to_add = $("option:selected", select_condition_element).text();
  let type_id = $("option:selected", select_entity_element).attr("type_id");
  let type_entity =
    $("option:selected", select_type_element).text() +
    " " +
    $("option:selected", select_entity_element).text();
  if ($("#conditions_grid " + "#" + condition_to_add).length) {
    let condition_box_element = $("#" + condition_to_add + "_box");
    let index = 1;
    while (
      $("#" + condition_to_add + "_box " + "#" + condition_to_add + "_" + index)
        .length
    ) {
      index++;
    }

    condition_box_element.append(
      `<p id="${condition_to_add}_${index}_AND" class="fs-6 fw-bold">AND</p>`,
    );

    condition_box_element.append(
      `<div id="${condition_to_add}_${index}">
        <div id="${condition_to_add}_${index}_text" type_id="${type_id}" class="fs-6">${type_entity}</div>
        <a class="col btn rounded-circle py-0 px-2 btn-danger text-white" role="button" onclick="remove_condition(this)">X</a>
      </div>`,
    );
  } else {
    let grid = $("#conditions_grid");
    if (condition_to_add !== "Condition1") {
      grid.append(
        `<div id="${condition_to_add}_OR" class="row">
            <div class="col">
                <div class="fs-6 fw-bold">OR</div>
                </div>
            </div>`,
      );
    }
    grid.append(
      `<div id="${condition_to_add}" class="row">
            <div class="col fs-5">
                ${condition_to_add}
            </div>
        </div>`,
    );
    grid.append(
      `<div id="${condition_to_add}_box" class="d-flex flex-row gap-2">
        <div id="${condition_to_add}_1">
            <div id="${condition_to_add}_1_text" type_id="${type_id}" class="fs-6">
                ${type_entity}
            </div>
            <a class="col btn rounded-circle py-0 px-2 btn-danger text-white" role="button" onclick="remove_condition(this)">X</a>
        </div>
      </div>`,
    );
    select_condition_updater();
  }
});

function remove_condition(element) {
  element = $(element);
  let parent = element.parent();
  let id_index = parent.attr("id").split("_", 2);
  let condition = id_index[0];
  let condition_num = condition.charAt(condition.length - 1);
  let index = id_index[1];
  let and_element = $("#" + parent.attr("id") + "_" + "AND");
  if (and_element.length) {
    and_element.remove();
  }
  parent.remove();
  index++;
  let cur_condition_elem = $("#" + condition + "_" + index);
  while (cur_condition_elem.length) {
    and_element = $("#" + condition + "_" + index + "_" + "AND");
    if (and_element.length && index - 1 === 1) {
      and_element.remove();
    } else if (and_element.length) {
      and_element.attr("id", condition + "_" + (index - 1) + "_" + "AND");
    }
    $(`#${cur_condition_elem.attr("id")}_text`).attr(
      "id",
      condition + "_" + (index - 1) + "_text",
    );
    cur_condition_elem.attr("id", condition + "_" + (index - 1));
    index++;
    cur_condition_elem = $("#" + condition + "_" + index);
  }

  if (!$("#" + condition + "_" + 1).length) {
    $("#" + condition + "_box").remove();
    $("#" + condition).remove();
    let or_element = $("#" + condition + "_OR");
    if (or_element.length) {
      or_element.remove();
    }
    condition_num++;
    while ($("#Condition" + condition_num).length) {
      let elements_to_update = $(`[id^=Condition${condition_num}]`);
      for (let i = 0; i < elements_to_update.length; i++) {
        element = $(elements_to_update.get(i));
        or_element = $("#Condition" + condition_num + "_" + "OR");
        if (or_element.length && condition_num - 1 === 1) {
          or_element.remove();
        }
        let index = element.attr("id").indexOf("_");
        let condition_rest = [
          element.attr("id").substr(0, index),
          element.attr("id").substr(index + 1),
        ];
        if (index !== -1) {
          element.attr(
            "id",
            "Condition" + (condition_num - 1) + "_" + condition_rest[1],
          );
        } else {
          element.attr("id", "Condition" + (condition_num - 1));
          $("#Condition" + (condition_num - 1))
            .children("div")
            .text("Condition" + (condition_num - 1));
        }
      }
      condition_num++;
    }
    select_condition_updater();
  }
}

function aup_list_click(element) {
  element = $(element);
  element = element.children("i");
  element.toggleClass("fa-caret-down");
  element.toggleClass("fa-caret-up");
}

function edit_name_click(btn) {
  btn = $(btn);
  let aup_index = btn.parents(".collapse").attr("id"); //aupX
  let index = aup_index.substring(3);
  let aup = aups_dict["enabled"][index];
  let modal = $("#edit_name_modal");
  modal.attr("aup_index", index);
  $("#edit_name_cur_name").text("Current name: " + aup.name);
  let input = $("#edit_name_input");
  input.val("");
  input.removeClass("is-invalid");
  modal.modal("show");
}

function edit_name_save() {
  let input = $("#edit_name_input");
  if (input.val() === "") {
    input.addClass("is-invalid");
  } else {
    input.removeClass("is-invalid");
    let modal = $("#edit_name_modal");
    let aup_index = modal.attr("aup_index");
    $.ajax({
      url: "/update_aup_name",
      dataType: "json",
      type: "post",
      contentType: "application/json",
      data: JSON.stringify({
        _id: aups_dict["enabled"][aup_index]._id,
        new_name: input.val(),
      }),
      processData: false,
      success: function () {
        aups_dict["enabled"][aup_index].name = input.val();
        let aup_item = $("#item_aup" + aup_index);
        aup_item.text(
          input.val() + " v" + aups_dict["enabled"][aup_index].version,
        );
        aup_item.append('<i class="fa-solid fa-caret-down float-end"></i>');
        for (let i = 0; i < aups_dict["enabled"].length; i++) {
          if (
            i !== aup_index &&
            aups_dict["enabled"][i].actual_aup_id ===
              aups_dict["enabled"][aup_index]._id
          ) {
            aup_item = $("#item_aup" + i);
            if (aup_item.length) {
              aup_item.text(
                input.val() + " v" + aups_dict["enabled"][i].version,
              );
              aup_item.append(
                '<i class="fa-solid fa-caret-down float-end"></i>',
              );
            }
          }
        }
        alert("Aup name was successfully updated.");
      },
      error: function (jqXhr, textStatus, errorThrown) {
        alert("Error occurred");
        console.log(errorThrown);
      },
    });
    modal.modal("hide");
  }
}

function edit_content_click(btn) {
  btn = $(btn);
  let aup_index = btn.parents(".collapse").attr("id"); //aupX
  let index = aup_index.substring(3);
  let aup = aups_dict["enabled"][index];
  let modal = $("#edit_content_modal");
  modal.attr("aup_index", index);
  editor.setMarkdown(aup.markdown);
  $("#edit_content_modal_empty").addClass("d-none");
  modal.modal("show");
}

function generate_aup_conditions_html(aup_index, aup) {
  let con_box = $(`#aup${aup_index}_con_box`);
  if (!con_box.length) {
    return;
  }
  con_box.children().remove();
  for (let outer = 0; outer < aup.conditions.length; outer++) {
    for (let inner = 0; inner < aup.conditions[outer].length; inner++) {
      con_box.append(
        `<div id="aup${aup_index}_con${outer}_${inner}">
                    <div id="aup${aup_index}_con${outer}_${inner}_text" class="fs-6">
                    </div>
                </div>`,
      );
      let text_ent = $(`#aup${aup_index}_con${outer}_${inner}_text`);
      if (inner === 0 && aup.conditions.length !== 1) {
        text_ent.text(`(`);
      }
      text_ent.text(
        `${text_ent.text()} ${aup.conditions[outer][inner].type} ${
          aup.conditions[outer][inner].name
        }`,
      );
      if (
        inner === aup.conditions[outer].length - 1 &&
        aup.conditions.length !== 1
      ) {
        text_ent.text(`${text_ent.text()} )`);
      }
      if (inner < aup.conditions[outer].length - 1) {
        con_box.append(
          `<p id="aup${aup_index}_con${outer}_${inner + 1}_AND"
                    class="fs-6 fw-bold">AND
                  </p>`,
        );
      }
    }
    if (outer < aup.conditions.length - 1) {
      con_box.append(
        `<p id="aup${aup_index}_con${outer + 1}_OR"
                    class="fs-6 fw-bold">OR
                  </p>`,
      );
    }
  }
}

function edit_content_save() {
  if (editor.getMarkdown() === "") {
    $("#edit_content_modal_empty").removeClass("d-none");
  } else {
    $("#edit_content_modal_empty").addClass("d-none");
    let modal = $("#edit_content_modal");
    let aup_index = modal.attr("aup_index");
    $.ajax({
      url: "/update_aup_content",
      dataType: "json",
      type: "post",
      contentType: "application/json",
      data: JSON.stringify({
        _id: aups_dict["enabled"][aup_index]._id,
        content: editor.getMarkdown(),
      }),
      processData: false,
      success: function (new_aup) {
        let new_index = aups_dict["enabled"].length;
        new_aup.conditions = aups_dict["enabled"][aup_index].conditions;
        aups_dict["enabled"].push(new_aup);
        $(`#aup${aup_index}_edit_name`).addClass("d-none");
        $(`#aup${aup_index}_edit_content`).addClass("d-none");
        $(`#aup${aup_index}_edit_conditions`).addClass("d-none");
        $(`#aup${aup_index}_edit_msg`).removeClass("d-none");
        aups_dict["enabled"][aup_index].actual_aup_id = new_aup._id;
        for (let i = 0; i < aups_dict["enabled"].length; i++) {
          if (
            aups_dict["enabled"][i].actual_aup_id ===
            aups_dict["enabled"][aup_index]._id
          ) {
            aups_dict["enabled"][i].actual_aup_id = new_aup._id;
          }
        }
        let aup_list = $("#aup_list_enabled");
        aup_list.append(
          `<a id="item_aup${new_index}" class="list-group-item list-group-item-action text-center"
               data-bs-toggle="collapse"
               onclick="aup_list_click(this)"
               href="#aup${new_index}">
               ${new_aup.name} v${new_aup.version}
               <i class="fa-solid fa-caret-down float-end"></i>
           </a>`,
        );
        aup_list.append(
          `<div class="collapse" id="aup${new_index}">
               <div class="card card-body container">
                   <div class="container">
                       <div id="aup${new_index}_edit_msg"
                            class="row text-center d-none">
                            <span class="fs-5 text-danger">Old version, can not be edited</span>
                       </div>
                       <div class="row">
                           <div class="col">
                               <span class="fs-5">Conditions</span>
                               <div id="aup${new_index}_con_box" class="d-flex flex-row gap-2"></div>
                           </div>
                           <div class="d-flex flex-column col-2 gap-1">
                               <a id="aup${new_index}_edit_name"
                                   class="row btn btn-primary btn-sm align-middle rounded-pill float-end"
                                   onclick="edit_name_click(this)"
                                   role="button">
                                   Edit Name
                               </a>
                               <a id="aup${new_index}_edit_content"
                                  class="row btn btn-primary btn-sm align-middle rounded-pill float-end"
                                  onclick="edit_content_click(this)"
                                  role="button">
                                  Edit Content
                               </a>
                               <a id="aup${new_index}_edit_conditions"
                                   class="row btn btn-primary btn-sm align-middle rounded-pill float-end"
                                   onclick="edit_conditions_click(this)"
                                   role="button">
                                   Edit Conditions
                               </a>
                               <a id="delete_aup"
                                  class="row btn btn-danger btn-sm align-middle rounded-pill float-end mb-2"
                                  onclick="delete_aup_click(this)"
                                  role="button">
                                  Delete AUP
                               </a>
                           </div>
                       </div>
                       <div class="row fs-5 mt-1 ms-0">Content</div>
                       <div class="row card card-body">
                          ${new_aup.html}
                       </div>
                   </div>
               </div>
          </div>`,
        );
        generate_aup_conditions_html(new_index, new_aup);
        alert("New version of AUP was successfully created");
      },
      error: function (jqXhr, textStatus, errorThrown) {
        alert("Error occurred");
        console.log(errorThrown);
      },
    });
    modal.modal("hide");
  }
}

function edit_conditions_click(btn) {
  btn = $(btn);
  let aup_index = btn.parents(".collapse").attr("id"); //aupX
  let index = aup_index.substring(3);
  let aup = aups_dict["enabled"][index];
  let modal = $("#edit_conditions_modal");
  modal.attr("aup_index", index);
  let grid = $("#conditions_grid");
  grid.children().remove();
  for (let outer = 1; outer < aup.conditions.length + 1; outer++) {
    if (outer !== 1) {
      grid.append(
        `<div id="Condition${outer}_OR" class="row">
            <div class="col">
                <div class="fs-6 fw-bold">OR</div>
                </div>
            </div>`,
      );
    }
    grid.append(
      `<div id="Condition${outer}" class="row">
            <div class="col fs-5">
                Condition${outer}
            </div>
        </div>
        <div id="Condition${outer}_box" class="d-flex flex-row gap-2">
        </div>`,
    );
    let cond_box = $(`#Condition${outer}_box`);
    for (let inner = 1; inner < aup.conditions[outer - 1].length + 1; inner++) {
      if (inner !== 1) {
        cond_box.append(
          `<p id="Condition${outer}_${inner}_AND" class="fs-6 fw-bold">AND</p>`,
        );
      }
      cond_box.append(
        `<div id="Condition${outer}_${inner}">
            <div id="Condition${outer}_${inner}_text" type_id="${
              aup.conditions[outer - 1][inner - 1].type_id
            }" class="fs-6">
                ${aup.conditions[outer - 1][inner - 1].type} ${
                  aup.conditions[outer - 1][inner - 1].name
                }
            </div>
            <a class="col btn rounded-circle py-0 px-2 btn-danger text-white" role="button" onclick="remove_condition(this)">X</a>
          </div>`,
      );
    }
  }
  select_condition_updater();
  $("empty_conditions").removeClass("d-none");
  modal.modal("show");
}

function edit_save_conditions() {
  let empty_conditions = $("#empty_conditions");
  if (!$("#Condition1").length) {
    empty_conditions.removeClass("d-none");
  } else {
    empty_conditions.addClass("d-none");
    let conditions = build_condition_to_save();
    let modal = $("#edit_conditions_modal");
    let aup_index = modal.attr("aup_index");
    let aup_id = aups_dict["enabled"][aup_index]._id;
    $.ajax({
      url: "/update_aup_conditions",
      dataType: "json",
      type: "post",
      contentType: "application/json",
      data: JSON.stringify({
        _id: aup_id,
        conditions: conditions,
      }),
      processData: false,
      success: function () {
        aups_dict["enabled"][aup_index].conditions = conditions;
        generate_aup_conditions_html(
          aup_index,
          aups_dict["enabled"][aup_index],
        );
        for (let i = 0; i < aups_dict["enabled"].length; i++) {
          if (aups_dict["enabled"][i].actual_aup_id === aup_id) {
            aups_dict["enabled"][i].conditions = conditions;
            generate_aup_conditions_html(i, aups_dict["enabled"][i]);
          }
        }
        alert("Aup conditions were successfully updated.");
      },
      error: function (jqXhr, textStatus, errorThrown) {
        alert("Error occurred");
        console.log(errorThrown);
      },
    });
    modal.modal("hide");
  }
}

function delete_aup_click(btn) {
  btn = $(btn);
  let aup_index = btn.parents(".collapse").attr("id"); //aupX
  let index = aup_index.substring(3);
  let aup = aups_dict["enabled"][index];
  let modal = $("#delete_aup_modal");
  modal.attr("aup_index", index);
  $("#delete_aup_msg").text(
    `Do you really want delete aup: ${aup.name} v${aup.version}`,
  );
  modal.modal("show");
}

function delete_aup_perform() {
  let modal = $("#delete_aup_modal");
  let aup_index = modal.attr("aup_index");
  let aup_id = aups_dict["enabled"][aup_index]._id;
  $.ajax({
    url: "/delete_aup",
    dataType: "json",
    type: "post",
    contentType: "application/json",
    data: JSON.stringify({
      _id: aup_id,
    }),
    processData: false,
    success: function (response) {
      $(`#item_aup${aup_index}`).remove();
      $(`#aup${aup_index}`).remove();
      let new_actual_aup_id = response["new_actual_aup_id"];
      if (new_actual_aup_id != null) {
        for (let i = 0; i < aups_dict["enabled"].length; i++) {
          if (aups_dict["enabled"][i]._id === new_actual_aup_id) {
            aups_dict["enabled"][i].actual_aup_id = null;
            $(`#aup${i}_edit_name`).removeClass("d-none");
            $(`#aup${i}_edit_content`).removeClass("d-none");
            $(`#aup${i}_edit_conditions`).removeClass("d-none");
            $(`#aup${i}_edit_msg`).addClass("d-none");
          } else if (aups_dict["enabled"][i].actual_aup_id === aup_id) {
            aups_dict["enabled"][i].actual_aup_id = new_actual_aup_id;
          }
        }
      }
      alert("Aup was successfully deleted.");
    },
    error: function (jqXhr, textStatus, errorThrown) {
      alert("Error occurred");
      console.log(errorThrown);
    },
  });
  modal.modal("hide");
}

function search_aups(search_input) {
  search_input = $(search_input);
  let search_str = search_input.val().toLowerCase();
  for (let i = 0; i < aups_dict["enabled"].length; i++) {
    let aup_item_entity = $("#item_aup" + i);
    if (aup_item_entity.length) {
      if (aups_dict["enabled"][i].name.toLowerCase().includes(search_str)) {
        aup_item_entity.removeClass("d-none");
      } else {
        aup_item_entity.addClass("d-none");
        $(`#aup${i}`).removeClass("show");
      }
    }
  }
  for (let i = 0; i < aups_dict["disabled"].length; i++) {
    let aup_item_entity = $("#item_aup" + i + "_disabled");
    if (aup_item_entity.length) {
      if (aups_dict["disabled"][i].name.toLowerCase().includes(search_str)) {
        aup_item_entity.removeClass("d-none");
      } else {
        aup_item_entity.addClass("d-none");
      }
    }
  }
}

function accept_aup_continue(button) {
  button = $(button);
  let splitted = button.attr("id").split("_");
  let index = parseInt(splitted[splitted.length - 1]);
  let current_stepper = $(`#accept_aup_stepper_${index}`);
  current_stepper.removeClass("bg-primary");
  current_stepper.addClass("bg-success");
  let next_stepper = $(`#accept_aup_stepper_${index + 1}`);
  next_stepper.removeClass("bg-secondary");
  next_stepper.addClass("bg-primary");
  $(`#accept_aup_${index}`).addClass("d-none");
  $(`#accept_aup_${index + 1}`).removeClass("d-none");
}

function accept_aup_back(button) {
  button = $(button);
  let splitted = button.attr("id").split("_");
  let index = parseInt(splitted[splitted.length - 1]);
  let current_stepper = $(`#accept_aup_stepper_${index}`);
  current_stepper.removeClass("bg-primary");
  current_stepper.addClass("bg-secondary");
  let prev_stepper = $(`#accept_aup_stepper_${index - 1}`);
  prev_stepper.removeClass("bg-success");
  prev_stepper.addClass("bg-primary");
  $(`#accept_aup_${index}`).addClass("d-none");
  $(`#accept_aup_${index - 1}`).removeClass("d-none");
}
