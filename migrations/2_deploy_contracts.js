// import vyper artifacts
const ERC20 = artifacts.require('ERC20.vyper');
const Kernel = artifacts.require('kernel.vyper');
const Position = artifacts.require('position.vyper');
const Protocol = artifacts.require('protocol.vyper');

module.exports = function(deployer, network, accounts) {
  if (network == "wrangler_development") {
    var lenderAddress = accounts[1],
      borrowerAddress = accounts[2],
      wranglerAddress = accounts[3],
      protocolContractInstance, protocolTokenContractInstance,
      kernelTemplateContractInstance, positionTemplateContractInstance,
      daiContractInstance, wethContractInstance;

    deployer.deploy(ERC20, "Lendroid Support Token", "LST", 18, 12000000000)
    .then(function(tokenContract) {
      console.log("Lendroid Support Token contract has been deployed");
      protocolTokenContractInstance = tokenContract
      return deployer.deploy(Kernel)
    }).then(function(kernelTemplateContract) {
      console.log("Kernel template contract has been deployed");
      kernelTemplateContractInstance = kernelTemplateContract
      return deployer.deploy(Position)
    }).then(function(positionTemplateContract) {
      console.log("Position template contract has been deployed");
      positionTemplateContractInstance = positionTemplateContract
      return deployer.deploy(Protocol, protocolTokenContractInstance.address, kernelTemplateContractInstance.address, positionTemplateContractInstance.address)
    }).then(function(protocolContract) {
      console.log("Vyper Protocol contract has been deployed");
      protocolContractInstance = protocolContract;
      return deployer.deploy(ERC20, "DAI Stablecoin", "DAI", 18, 12000000000)
    }).then(function(daiContract) {
      console.log("DAI Stablecoin contract has been deployed");
      daiContractInstance = daiContract;
      return deployer.deploy(ERC20, "Wrapped ETH", "WETH", 18, 12000000000)
    }).then(function(wethContract) {
      console.log("WETH contract has been deployed");
      wethContractInstance = wethContract;
      return protocolContractInstance.set_token_support(daiContractInstance.address, true)
    }).then(function(txResult) {
      console.log("DAI Stablecoin supported");
      return protocolContractInstance.set_token_support(wethContractInstance.address, true)
    }).then(function(txResult) {
      console.log("WETH supported");
      return protocolContractInstance.set_wrangler_status(wranglerAddress, true)
    }).then(function(txResult) {
      console.log(`Wrangler ${wranglerAddress} supported`);
      return daiContractInstance.transfer(lenderAddress, "100000000000000000000")
    }).then(function(txResultDAITransfer) {
      console.log(`Lender ${lenderAddress} has 100 DAI Stablecoin`);
      return wethContractInstance.transfer(borrowerAddress, "100000000000000000000")
    }).then(function(txResultWETHTransfer) {
      console.log(`Borrower ${borrowerAddress} has 100 WETH`);
      return protocolTokenContractInstance.transfer(lenderAddress, "100000000000000000000")
    }).then(function(txResultLSTTransferToLender) {
      console.log(`Lender has 100 LST`);
      return protocolTokenContractInstance.transfer(borrowerAddress, "100000000000000000000")
    }).then(function(txResultLSTTransferToBorrower) {
      console.log(`Borrower has 100 LST`);
      return protocolTokenContractInstance.approve(protocolContractInstance.address, "10000000000000000000", {from: borrowerAddress})
    }).then(function(txResultLSTApprovalByBorrower) {
      console.log(`Borrower has approved 10 LST`);
      return wethContractInstance.approve(protocolContractInstance.address, "10000000000000000000", {from: borrowerAddress})
    }).then(function(txResultWETHApprovalByBorrower) {
      console.log(`Borrower has approved 10 WETH`);
      return protocolTokenContractInstance.approve(protocolContractInstance.address, "10000000000000000000", {from: lenderAddress})
    }).then(function(txResultLSTApprovalByLender) {
      console.log(`Lender has approved 10 LST`);
      return daiContractInstance.approve(protocolContractInstance.address, "10000000000000000000", {from: lenderAddress})
    }).then(function(txResultDAIApprovalByLender) {
      console.log(`Lender has approved 10 DAI Stablecoin`);
    });
  }
  else {
    var protocolTokenContractInstance, kernelTemplateContractInstance, positionTemplateContractInstance;
    deployer.deploy(ERC20, "Lendroid Support Token", "LST", 18, 12000000000)
    .then(function(tokenContract) {
      console.log("Lendroid Support Token contract has been deployed");
      protocolTokenContractInstance = tokenContract
      return deployer.deploy(Kernel)
    }).then(function(kernelTemplateContract) {
      console.log("Kernel template contract has been deployed");
      kernelTemplateContractInstance = kernelTemplateContract
      return deployer.deploy(Position)
    }).then(function(positionTemplateContract) {
      console.log("Position template contract has been deployed");
      positionTemplateContractInstance = positionTemplateContract
      return deployer.deploy(Protocol, protocolTokenContractInstance.address, kernelTemplateContractInstance.address, positionTemplateContractInstance.address)
    }).then(function(protocolContract) {
      console.log("Vyper Protocol contract has been deployed");
    });
  }
};
