exports.handler = async (event) => {
    const requestBody = JSON.parse(event.body);
    const response = {
        statusCode: 200,
        body: JSON.stringify({
            message: "Request received",
            data: requestBody,
        }),
    };
    return response;
};
