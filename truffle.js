module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*" // Match any network id
    },
    wrangler_development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "101",
      gas: 6250000
    }
  }
};
