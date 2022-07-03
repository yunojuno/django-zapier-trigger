const subscription = require("./subscription");
const EVENT_NAME = "new_book";

module.exports = {
    key: EVENT_NAME,
    noun: "Book",
    display: {
        label: "New Book",
        description: "Triggers when a book is published.",
        hidden: false,
        important: true
    },
    operation: {
        type: "hook",
        perform: subscription.perform(EVENT_NAME),
        performList: subscription.list(EVENT_NAME),
        performSubscribe: subscription.subscribe(EVENT_NAME),
        performUnsubscribe: subscription.unsubscribe(EVENT_NAME),
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
