/**
 * Node-RED Settings
 * Configure Node-RED for running behind a proxy
 */
module.exports = {
    // Set httpRoot to the path where Node-RED is mounted
    httpAdminRoot: '/node-red',
    httpNodeRoot: '/node-red',
    
    // Disable strict MIME checking
    requireHttps: false,
    disableEditor: false,
    httpStaticRoot: '/node-red/static/',
    
    // This prevents 404s with assets
    httpNodeCors: {
        origin: "*",
        methods: "GET,PUT,POST,DELETE"
    },
    
    // Other standard settings
    functionGlobalContext: {},
}; 