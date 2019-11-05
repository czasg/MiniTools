import execjs

__all__ = "get_anti_spider_clearance",


def get_anti_spider_clearance(js_string):
    script_content = r"""
var window = {
 headless: NaN
}
var get_cookie = function(js_code) {
    var re = /var.*?pop\(\)\);/
    args = re.exec(js_code)[0]
    eval(args)

	var func = (xxx) => {
	    var aim = y.replace(/\b\w+\b/g, (y) => {
            return x[f(y, xxx) - 1] || ("_" + y)
	    });
	    return aim;
	};

    while (1){
        aim = func(z)
        if (aim.indexOf("document.cookie") != -1){
            doc = aim;
            break
        }else{
            z += 1
        }
    }

    var re = /document.cookie='(.*?)\+';Expires/
    cookie = re.exec(doc)[1]

    var re = /.*?'\+(.*)/;
    key = re.exec(cookie)[1]
    cookie = cookie.replace("'\+" + key, eval(key))
    return cookie
}
"""
    anti_js = execjs.compile(script_content)
    return anti_js.call("get_cookie", js_string)
