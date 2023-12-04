
window.onload=function()
{
    fetch("file://./country_vs_code.csv")
    .then((res) => res.text())
    .then((text) => {
      // do something with "text"
     })
    .catch((e) => console.error(e));
};