"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("student-form");
    if (!form) return;

    const list = document.getElementById("student-list");
    const message = document.getElementById("message");
    const search = document.getElementById("student-search");
    const count = document.getElementById("student-count");
    const recordCount = document.getElementById("record-count");
    const visibleCount = document.getElementById("visible-count");
    const heading = document.getElementById("form-heading");
    const submitButton = document.getElementById("submit-student");
    const cancelButton = document.getElementById("cancel-edit");
    const role = document.body.dataset.role;
    let students = [];
    let editingId = null;

    async function api(url, options = {}) {
        const headers = { ...(options.headers || {}) };
        if (options.body) headers["Content-Type"] = "application/json";

        const response = await fetch(url, {
            ...options,
            headers,
            credentials: "same-origin"
        });

        const contentType = response.headers.get("content-type") || "";
        const data = contentType.includes("application/json")
            ? await response.json()
            : {};

        if (!response.ok) {
            throw new Error(data.error || `Request failed (${response.status})`);
        }
        return data;
    }

    function showMessage(text, isError = false) {
        message.textContent = text;
        message.classList.toggle("is-error", isError);
    }

    function makeCell(text, className = "") {
        const cell = document.createElement("td");
        cell.textContent = text ?? "";
        if (className) cell.className = className;
        return cell;
    }

    function makeAction(label, action, id, className) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = label;
        button.dataset.action = action;
        button.dataset.id = String(id);
        button.className = `button ${className} button-small`;
        return button;
    }

    function renderStudents() {
        const query = (search.value || "").trim().toLowerCase();
        const filtered = students.filter(student =>
            [student.name, student.email, student.course]
                .some(value => String(value).toLowerCase().includes(query))
        );

        list.replaceChildren();

        if (filtered.length === 0) {
            const row = document.createElement("tr");
            row.className = "empty-row";
            const cell = document.createElement("td");
            cell.colSpan = 4;
            const empty = document.createElement("div");
            empty.className = "empty-state";
            const icon = document.createElement("span");
            icon.setAttribute("aria-hidden", "true");
            icon.textContent = "▤";
            const title = document.createElement("strong");
            title.textContent = query ? "No matching students" : "No students yet";
            const detail = document.createElement("p");
            detail.textContent = query
                ? "Try a different search term."
                : "Add a student using the form to get started.";
            empty.append(icon, title, detail);
            cell.appendChild(empty);
            row.appendChild(cell);
            list.appendChild(row);
        } else {
            for (const student of filtered) {
                const row = document.createElement("tr");
                row.dataset.id = String(student.id);

                const studentCell = document.createElement("td");
                const name = document.createElement("span");
                name.className = "student-name";
                name.textContent = student.name;
                const id = document.createElement("small");
                id.className = "student-id";
                id.textContent = `ID #${student.id}`;
                studentCell.append(name, id);

                const courseCell = makeCell("");
                const course = document.createElement("span");
                course.className = "course-pill";
                course.textContent = student.course;
                courseCell.appendChild(course);

                const actions = document.createElement("td");
                actions.className = "row-actions";
                actions.appendChild(makeAction("Edit", "edit", student.id, "button-quiet"));
                if (role === "admin") {
                    actions.appendChild(makeAction("Delete", "delete", student.id, "button-danger-quiet"));
                }

                row.append(studentCell, makeCell(student.email), courseCell, actions);
                list.appendChild(row);
            }
        }

        count.textContent = String(students.length);
        recordCount.textContent = `${students.length} ${students.length === 1 ? "record" : "records"}`;
        visibleCount.textContent = `Showing ${filtered.length} of ${students.length} students`;
    }

    async function refreshStudents() {
        students = await api("/api/students");
        renderStudents();
    }

    function resetForm() {
        form.reset();
        editingId = null;
        heading.textContent = "Add a student";
        submitButton.textContent = "Add student";
        cancelButton.hidden = true;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        const data = Object.fromEntries(new FormData(form));
        const isEditing = editingId !== null;
        const url = isEditing ? `/api/students/${editingId}` : "/api/students";

        submitButton.disabled = true;
        submitButton.textContent = isEditing ? "Saving..." : "Adding...";
        try {
            await api(url, {
                method: isEditing ? "PUT" : "POST",
                body: JSON.stringify(data)
            });
            resetForm();
            await refreshStudents();
            showMessage(isEditing ? "Student updated successfully." : "Student added successfully.");
        } catch (error) {
            showMessage(error.message || "Unable to save student.", true);
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = editingId !== null ? "Save changes" : "Add student";
        }
    });

    cancelButton.addEventListener("click", () => {
        resetForm();
        showMessage("");
    });

    list.addEventListener("click", async event => {
        const button = event.target.closest("button[data-action]");
        if (!button) return;

        const id = Number(button.dataset.id);
        const student = students.find(item => item.id === id);
        if (!student) {
            showMessage("This student record could not be found. Refresh and try again.", true);
            return;
        }

        if (button.dataset.action === "edit") {
            editingId = id;
            form.elements.name.value = student.name;
            form.elements.email.value = student.email;
            form.elements.course.value = student.course;
            heading.textContent = "Edit student";
            submitButton.textContent = "Save changes";
            cancelButton.hidden = false;
            showMessage("Editing student details.");
            form.elements.name.focus();
            form.scrollIntoView({ behavior: "smooth", block: "center" });
            return;
        }

        if (button.dataset.action === "delete") {
            if (role !== "admin") {
                showMessage("Only an admin can delete student records.", true);
                return;
            }
            if (!window.confirm(`Delete the record for ${student.name}? This cannot be undone.`)) return;

            button.disabled = true;
            try {
                await api(`/api/students/${id}`, { method: "DELETE" });
                if (editingId === id) resetForm();
                await refreshStudents();
                showMessage("Student deleted successfully.");
            } catch (error) {
                showMessage(error.message || "Unable to delete student.", true);
                button.disabled = false;
            }
        }
    });

    search.addEventListener("input", renderStudents);

    refreshStudents().catch(error => {
        showMessage(error.message || "Could not load student records. Please reload the page.", true);
    });
});
