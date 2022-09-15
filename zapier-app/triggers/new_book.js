const trigger = require("./trigger");

module.exports = {
    key: "new_book",
    noun: "Book",
    display: {
        label: "New Book",
        description: "Triggers when a book is published.",
        hidden: false,
        important: true
    },
    operation: {
        type: "hook",
        perform: trigger.perform("new_book"),
        performList: trigger.sample("new_book"),
        performSubscribe: trigger.subscribe("new_book"),
        performUnsubscribe: trigger.unsubscribe("new_book"),
        sample: {
            id: 1,
            author: "Arthur Conan Doyle",
            title: "Hound of the Baskervilles",
            published: 1902
        },
        // override the label to make it more meaningful
        outputFields: [
            { key: "published", label: "Year of publication" }
        ]
    }
};
