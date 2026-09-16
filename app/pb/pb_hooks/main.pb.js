console.log('LOADING', 'app/pb/pb_hooks/main.pb.js');
/// <reference path="../pb_data/types.d.ts" />



routerAdd("GET", "/api/test-artifacts", (e) => {
    return e.json(200, { message: "API works!" });
});
