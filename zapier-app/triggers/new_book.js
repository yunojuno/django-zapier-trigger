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
            id: "123456",
            authorName: "Arthur Conan Doyle",
            bookTitle: "Hound of the Baskervilles",
            publishedYear: 1902
        }
    }
};
