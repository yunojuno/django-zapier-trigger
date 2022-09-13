const trigger = require("./trigger");

module.exports = {
    key: "new_film",
    noun: "Film",
    display: {
        label: "New Film",
        description: "Triggers when a new film is released (polling).",
        hidden: false,
        important: true
    },
    operation: {
        perform: trigger.list("new_film"),
        sample: {
            id: 1,
            title: "Sergei Eisenstein",
            director: "Ivan the Terrible",
            release_date: "1944-12-30"
        }
    }
};
