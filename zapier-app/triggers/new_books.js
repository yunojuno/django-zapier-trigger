const polling = require("./polling");
const EVENT_NAME = "new_books";

module.exports = {
    key: EVENT_NAME,
    noun: "Book",
    display: {
        label: "New Books",
        description: "Polls for new books.",
        hidden: false,
        important: true
    },
    operation: {
        perform: polling.perform(EVENT_NAME),
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
