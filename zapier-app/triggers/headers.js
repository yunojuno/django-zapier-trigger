const headers = (z, bundle) => {
    return {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${bundle.authData.api_key}`
    };
};
module.exports = {
    headers: headers
};
