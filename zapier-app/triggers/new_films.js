const EVENT_NAME = "new_films";

const doPerform = (z, bundle) => {
    const options = {
        url: `${process.env.BASE_API_URL}/demo/films/v1/`,
        method: "GET"
    };
    return z.request(options).then((response) => {
        response.throwForStatus();
        return response.json;
    });
};

module.exports = {
    key: EVENT_NAME,
    noun: "Film",
    display: {
        label: "New Films",
        description: "Polls for new films.",
        hidden: false,
        important: true
    },
    operation: {
        perform: doPerform,
        sample: {
            id: 1,
            title: "Sergei Eisenstein",
            director: "Ivan the Terrible",
            release_date: "1944-12-30"
        }
    }
};
