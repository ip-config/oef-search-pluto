
class CrawlerDisplay
{
    constructor(http, url, targetElementId)
    {
        var self = this;
        self.http = http;
        self.url = url;
        self.targetElementId = targetElementId;
    }

    tick()
    {
        var self = this;
        self.get();
    }

    get()
    {
        var self = this;
        let headers = {};

        self.http.get(self.url, {
            headers: headers,
        }).then((response) => {
            console.log(response);

            document.getElementById(self.targetElementId).innerHTML = response.data;

        }).catch((error) => {
            console.log("Denied:"+ fullurl+" because "+error);
        });
    }

    display()
    {
    }
}
