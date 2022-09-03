const subscription = require("./subscription");

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
        perform: subscription.perform,
        performList: subscription.list("new_book"),
        performSubscribe: subscription.subscribe("new_book"),
        performUnsubscribe: subscription.unsubscribe("new_book"),
        sample: {
            id: "123456",
            authorName: "Arthur Conan Doyle",
            bookTitle: "Hound of the Baskervilles",
            publishedYear: 1902
        }
    }
};
