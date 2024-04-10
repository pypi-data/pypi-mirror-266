/* global MyAMS */

'use strict';


if (window.$ === undefined) {
    window.$ = MyAMS.$;
}


const swagger = {

    initSwagger: () => {
        MyAMS.require({
            'swagger-ui': {
                src: '/--static--/pyams_zmi/js/swagger-ui-bundle.min.js',
                css: '/--static--/pyams_zmi/css/swagger-ui.min.css'
            },
            'swagger-preset': '/--static--/pyams_zmi/js/swagger-ui-standalone-preset.min.js'
        }).then(() => {
            window.ui = SwaggerUIBundle({
                url: "/__api__",
                dom_id: '#swagger-ui',
                docExpansion: "list",
                validatorUrl: null,
                deepLinking: false,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ]
                // layout: "StandaloneLayout"
            });
        });
    }
}


if (window.MyAMS) {
    MyAMS.config.modules.push('swagger');
    MyAMS.swagger = swagger;
    console.debug("MyAMS: swagger module loaded...");
}
