"use strict";
// Make eslint happy about the Window redefinition
(_) => null;
/**
 * Gets the value of a single cookie.
 *
 * @param name - Name of the cookie.
 * @return The cookie value, or null.
 */
function getCookie(name) {
    var _a;
    return (_a = document.cookie.split("; ")
        .find((row) => row.startsWith(`${name}=`))) === null || _a === void 0 ? void 0 : _a.split("=")[1];
}
/**
 * Builds a URL with the correct application URL as base.
 *
 * Do not add the leading slash, otherwise the resolution will be wrong!
 *
 * @param path - Path to append to the base.
 * @return The correct URL in regards to the application URL.
 */
function makeUrl(name) {
    return new URL(name, BASE_URL);
}
/**
 * Installs a listener to the given DOM objects.
 *
 * @param selector - The query selector to find the DOM objects.
 * @param event - The event name to listen to.
 * @param handler - The handler function.
 */
function addHandler(selector, event, handler) {
    document.querySelectorAll(selector).
        forEach((obj) => obj.addEventListener(event, handler));
}
/**
 * Handler for when a language is clicked. Sets the cookie to the correct locale.
 *
 * @param event - The triggering event.
 */
function languageClicked(event) {
    const path = new URL(BASE_URL).pathname;
    const language = event.target.getAttribute("data-langcode");
    document.cookie = `fietsboek_locale=${language}; Path=${path}`;
    window.location.reload();
    event.preventDefault();
}
addHandler(".language-choice", "click", languageClicked);
/**
 * Handler for when a tag is clicked. Removes the tag from the tag list.
 *
 * @param event - The triggering event.
 */
function tagClicked(event) {
    const span = event.target.closest('span');
    span.parentNode.removeChild(span);
}
addHandler(".tag-badge", "click", tagClicked);
/**
 * Handler to add a new tag when the button is pressed.
 */
function addTag() {
    var _a, _b;
    const newTag = document.querySelector("#new-tag");
    if (newTag.value === "") {
        return;
    }
    const node = document.createElement("span");
    node.classList.add("tag-badge");
    node.classList.add("badge");
    node.classList.add("rounded-pill");
    node.classList.add("bg-info");
    node.classList.add("text-dark");
    node.addEventListener("click", tagClicked);
    const text = document.createTextNode(newTag.value);
    node.appendChild(text);
    const icon = document.createElement("i");
    icon.classList.add("bi");
    icon.classList.add("bi-x");
    node.appendChild(icon);
    const input = document.createElement("input");
    input.hidden = true;
    input.name = "tag[]";
    input.value = newTag.value;
    node.appendChild(input);
    (_a = document.querySelector("#formTags")) === null || _a === void 0 ? void 0 : _a.appendChild(node);
    const space = document.createTextNode(" ");
    (_b = document.querySelector("#formTags")) === null || _b === void 0 ? void 0 : _b.appendChild(space);
    newTag.value = "";
}
addHandler("#add-tag-btn", "click", addTag);
// Also add a tag when enter is pressed
addHandler("#new-tag", "keypress", (event) => {
    if (event.code == "Enter") {
        event.preventDefault();
        addTag();
    }
});
/**
 * Function to check for password validity.
 *
 * @param main - Selector for the actual entered password input.
 * @param repeat - Selector for the repeated password, must match `main`.
 */
function checkPasswordValidity(main, repeat) {
    const mainPassword = document.querySelector(main);
    const repeatPassword = document.querySelector(repeat);
    const form = mainPassword.closest('form');
    form.classList.remove('was-validated');
    // Check password requirements. The validation errors are not actually
    // displayed, as the HTML template contains pre-filled texts for that.
    if (mainPassword.value.length != 0 && mainPassword.value.length < 8) {
        mainPassword.setCustomValidity('Too short');
    }
    else {
        mainPassword.setCustomValidity('');
    }
    if (mainPassword.value != repeatPassword.value) {
        repeatPassword.setCustomValidity('Needs to match');
    }
    else {
        repeatPassword.setCustomValidity('');
    }
}
// This function is used via a HTML onchange= handler, so make eslint happy
checkPasswordValidity;
/**
 * Function to check for name validity.
 *
 * @param name - Selector name that should be checked.
 */
function checkNameValidity(name) {
    const nameField = document.querySelector(name);
    if (nameField.value.length == 0) {
        nameField.setCustomValidity('Needs a name');
    }
}
// This function is used via a HTML onchange= handler, so make eslint happy
checkNameValidity;
/**
 * Check whether the given friend is already tagged.
 *
 * Note that this uses the "HTML list", so it uses the tags that the user is
 * currently editing - not the ones from the database!
 *
 * @param friendId - ID of the friend to check.
 * @return Whether the friend is in the list of tagged people.
 */
function friendIsTagged(friendId) {
    return Array.from(document.querySelectorAll("[name='tagged-friend[]']"))
        .map((obj) => obj)
        .filter((obj) => !obj.disabled)
        .map((obj) => obj.value)
        .includes(friendId.toString());
}
/**
 * Hit the endpoint to search for friends. This populates the friend selector
 * when tagging friends.
 */
function searchFriends() {
    const searchPattern = document.querySelector("#friendSearchQuery").
        value.toLowerCase();
    const friendSearch = document.querySelector("#friendSearch");
    friendSearch.innerHTML = "";
    fetch(FRIENDS_URL)
        .then((response) => response.json())
        .then((response) => {
        const blueprint = document.querySelector("#friendSearchBlueprint").content;
        // Only show friends with a matching name
        let friends = response.filter((obj) => obj.name.toLowerCase().indexOf(searchPattern) != -1);
        // Only show friends that are not yet existing
        friends = friends.filter((obj) => !friendIsTagged(obj.id));
        friends.forEach((friend) => {
            var _a;
            const copy = blueprint.cloneNode(true);
            copy.querySelector(".friend-name").textContent = friend.name;
            (_a = copy.querySelector("button")) === null || _a === void 0 ? void 0 : _a.addEventListener("click", (event) => {
                const button = event.target.closest("button");
                button.parentNode.parentNode.removeChild(button.parentNode);
                const added = document.querySelector("#friendAddedBlueprint")
                    .content
                    .cloneNode(true);
                added.querySelector(".friend-name").
                    textContent = friend.name;
                added.querySelector("input").value = friend.id.toString();
                added.querySelector("input").removeAttribute("disabled");
                added.querySelector("button").addEventListener("click", removeFriendClicked);
                document.querySelector('#taggedFriends').appendChild(added);
            });
            friendSearch.appendChild(copy);
        });
    });
}
addHandler("#add-friend-btn", "click", () => searchFriends());
// Also trigger the search on Enter keypress
addHandler("#friendSearchQuery", "keypress", (event) => {
    if (event.code == "Enter") {
        event.preventDefault();
        searchFriends();
    }
});
/**
 * Handler for when a "Remove friend" button is clicked.
 *
 * @param event - The triggering event.
 */
function removeFriendClicked(event) {
    const button = event.target.closest("button");
    button.parentNode.parentNode.removeChild(button.parentNode);
}
addHandler(".remove-friend-button", "click", removeFriendClicked);
/**
 * Handler for when the image input is changed.
 *
 * This handler splits the multiple images up into single input fields, such
 * that each one can be removed individually. It also adds preview images, and
 * adds the button to delete and edit the image's description.
 *
 * @param event - The triggering event.
 */
function imageSelectorChanged(event) {
    var _a;
    const target = event.target;
    for (const file of Array.from((_a = target.files) !== null && _a !== void 0 ? _a : [])) {
        window.fietsboekImageIndex++;
        const input = document.createElement("input");
        input.type = "file";
        input.hidden = true;
        input.name = `image[${window.fietsboekImageIndex}]`;
        const transfer = new DataTransfer();
        transfer.items.add(file);
        input.files = transfer.files;
        const preview = document.querySelector("#trackImagePreviewBlueprint").
            content.
            cloneNode(true);
        preview.querySelector("img").src = URL.createObjectURL(file);
        preview.querySelector("button.delete-image").
            addEventListener("click", deleteImageButtonClicked);
        preview.querySelector("button.edit-image-description").
            addEventListener("click", editImageDescriptionClicked);
        preview.querySelector("input.image-description-input").
            name = `image-description[${window.fietsboekImageIndex}]`;
        preview.querySelector("div").appendChild(input);
        document.querySelector("#trackImageList").appendChild(preview);
    }
    target.value = "";
}
addHandler("#imageSelector", "change", imageSelectorChanged);
/**
 * Handler to remove a picture from a track.
 *
 * @param event - The triggering event.
 */
function deleteImageButtonClicked(event) {
    const preview = event.target.closest("div.track-image-preview");
    /* If this was a image yet to be uploaded, simply remove it */
    const input = preview.querySelector("input[type=file]");
    if (input) {
        preview.parentNode.removeChild(preview);
        return;
    }
    /* Otherwise, we need to remove it but also insert a "delete-image" input */
    const deleter = preview.querySelector("input.image-deleter-input");
    deleter.removeAttribute("disabled");
    preview.removeChild(deleter);
    preview.parentNode.appendChild(deleter);
    preview.parentNode.removeChild(preview);
}
addHandler("button.delete-image", "click", deleteImageButtonClicked);
/**
 * Handler to show the image description editor.
 *
 * @param event - The triggering event.
 */
function editImageDescriptionClicked(event) {
    window.fietsboekCurrentImage = event.target.closest("div");
    const imageInput = window.fietsboekCurrentImage.querySelector("input.image-description-input");
    const currentDescription = imageInput.value;
    const modalDom = document.getElementById("imageDescriptionModal");
    modalDom.querySelector("textarea").value = currentDescription;
    const modal = bootstrap.Modal.getOrCreateInstance(modalDom, {});
    modal.show();
}
addHandler("button.edit-image-description", "click", editImageDescriptionClicked);
/**
 * Handler to save the image description of the currently edited image.
 *
 * @param event - The triggering event.
 */
function saveImageDescriptionClicked(_event) {
    const modalDom = document.getElementById("imageDescriptionModal");
    const wantedDescription = modalDom.querySelector("textarea").value;
    window.fietsboekCurrentImage.
        querySelector("input.image-description-input").
        value = wantedDescription;
    window.fietsboekCurrentImage.
        querySelector("img").title = wantedDescription;
    const modal = bootstrap.Modal.getOrCreateInstance(modalDom, {});
    modal.hide();
    window.fietsboekCurrentImage = null;
}
addHandler("#imageDescriptionModal button.btn-success", "click", saveImageDescriptionClicked);
/**
 * Handler to toggle (collapse/expand) the yearly/monthly summary.
 *
 * @param event - The triggering event.
 */
function toggleSummary(event) {
    const chevron = event.target;
    const containing = chevron.closest("a");
    const summary = containing.nextElementSibling;
    bootstrap.Collapse.getOrCreateInstance(summary).toggle();
    if (chevron.classList.contains("bi-chevron-down")) {
        chevron.classList.remove("bi-chevron-down");
        chevron.classList.add("bi-chevron-right");
    }
    else {
        chevron.classList.remove("bi-chevron-right");
        chevron.classList.add("bi-chevron-down");
    }
}
addHandler(".summary-toggler", "click", toggleSummary);
/*
 * Handler to enable the "Download archive button" ...
 */
addHandler("#archiveDownloadButton", "click", () => {
    const checked = document.querySelectorAll(".archive-checkbox:checked");
    const url = makeUrl("track/archive");
    checked.forEach((c) => {
        url.searchParams.append("track_id[]", c.value);
    });
    window.location.assign(url);
});
/*
 * ... and the listeners on the checkboxes to disable and enable the button.
 */
addHandler(".archive-checkbox", "change", () => {
    const checked = document.querySelectorAll(".archive-checkbox:checked");
    const downloadButton = document.querySelector("#archiveDownloadButton");
    downloadButton.disabled = (checked.length == 0);
});
/**
 * Handler to clear the input when a .button-clear-input is pressed.
 *
 * The button must be in an input-group with the input.
 *
 * @param event - The triggering event.
 */
function clearInputButtonClicked(event) {
    const target = event.target;
    target.closest(".input-group").querySelectorAll("input").forEach((i) => i.value = "");
    target.closest(".input-group").querySelectorAll("select").forEach((i) => i.value = "");
}
addHandler(".button-clear-input", "click", clearInputButtonClicked);
/**
 * Handler to change the sorting of the home page.
 *
 * This basically sets the cookie to signal that the home page should be
 * returned reversed, and then reloads the page.
 *
 * @param event - The triggering event.
 */
function changeHomeSorting(_event) {
    var _a;
    const currentSorting = (_a = getCookie("home_sorting")) !== null && _a !== void 0 ? _a : "asc";
    const newSorting = currentSorting == "asc" ? "desc" : "asc";
    document.cookie = `home_sorting=${newSorting}; SameSite=Lax`;
    window.location.reload();
}
addHandler("#changeHomeSorting", "click", changeHomeSorting);
/**
 * Handler to toggle the favourite status of a track.
 *
 * This is applied to .favourite-star elements and expects the track ID in
 * data-track-id.
 *
 * @param event - The triggering event.
 */
function toggleTrackFavourite(event) {
    var _a;
    const target = event.target;
    const trackId = target.getAttribute("data-track-id");
    if (trackId === null) {
        return;
    }
    const url = makeUrl("me/toggle-favourite");
    const formData = new URLSearchParams();
    formData.append("track-id", trackId);
    formData.append("csrf_token", (_a = getCookie("csrf_token")) !== null && _a !== void 0 ? _a : "");
    fetch(url, {
        "method": "POST",
        "body": formData,
    }).then(response => response.json().then(data => {
        const isNowFavourite = data["favourite"];
        if (isNowFavourite) {
            target.classList.replace("bi-star", "bi-star-fill");
        }
        else {
            target.classList.replace("bi-star-fill", "bi-star");
        }
    }));
}
addHandler(".favourite-star", "click", toggleTrackFavourite);
/**
 * Returns an array of localized month names (Jan-Dec).
 */
function getLocalizedMonthNames() {
    const monthNames = [];
    const date = new Date(2000, 0);
    for (let i = 0; i < 12; i++) {
        monthNames.push(date.toLocaleString(LOCALE, { month: 'long' }));
        date.setMonth(i + 1);
    }
    return monthNames;
}
/**
 * Load and plot the user's summary.
 */
function loadProfileStats() {
    const monthNames = getLocalizedMonthNames();
    const url = makeUrl("me/summary.json");
    fetch(url)
        .then(response => response.json())
        .then((response) => {
        const datasets = [];
        for (const [year, months] of Object.entries(response)) {
            const data = [];
            for (let i = 1; i <= 12; ++i) {
                data.push((i in months) ? (months[i] / 1000) : 0);
            }
            datasets.push({
                data: data,
                label: year,
            });
        }
        new Chart("graph-month-summary", {
            type: "bar",
            data: {
                datasets: datasets,
                labels: monthNames,
            },
        });
    });
}
/* Used via in-page scripts, so make eslint happy */
loadProfileStats;
document.addEventListener('DOMContentLoaded', function () {
    window.fietsboekImageIndex = 0;
    /* Enable tooltips */
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map((tooltipTriggerEl) => {
        return new bootstrap.Tooltip(tooltipTriggerEl, { sanitize: false });
    });
    /* Enable Bootstrap form validation */
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    /* Format all datetimes to the local timezone */
    document.querySelectorAll(".fietsboek-local-datetime").forEach((obj) => {
        const timestamp = parseFloat(obj.attributes.getNamedItem("data-utc-timestamp").value);
        const date = new Date(timestamp * 1000);
        // TypeScript complains about this, but according to MDN it is fine, at
        // least in "somewhat modern" browsers
        const intl = new Intl.DateTimeFormat(LOCALE, {
            dateStyle: "medium",
            timeStyle: "medium",
        });
        obj.innerHTML = intl.format(date);
    });
});
//# sourceMappingURL=fietsboek.js.map