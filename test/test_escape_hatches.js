// helpers
const mineTx = require("./helpers/mineTx.js");
// contracts
var ERC20 = artifacts.require('ERC20.vyper'),
  KernelTemplate = artifacts.require('kernel.vyper'),
  PositionTemplate = artifacts.require('position.vyper'),
  Protocol = artifacts.require('protocol.vyper');
// provider
const Web3 = require('web3');
const web3 = new Web3(new Web3.providers.HttpProvider("http://127.0.0.1:8545"))

contract("Protocol", function (addresses) {


  beforeEach(async function () {
    this.protocolToken = await ERC20.new("Lendroid Support Token", "LST", 18, 12000000000);
    this.LendToken = await ERC20.new("Test Lend Token", "TLT", 18, 1000000000);
    this.BorrowToken = await ERC20.new("Test Borrow Token", "TBT", 18, 1000000000);
    let KERNEL_TEMPLATE = await KernelTemplate.new(),
      POSITION_TEMPLATE = await PositionTemplate.new();
    this.protocolContract = await Protocol.new(this.protocolToken.address, KERNEL_TEMPLATE.address, POSITION_TEMPLATE.address);
  });


  it("protocol contract should not accept ether", async function() {
    assert.isTrue(web3.toDecimal(web3.eth.getBalance(this.protocolContract.address)) === 0, `protocol contract's initial balance should be 0 ether`)
    let errr = false
    try {
      web3.eth.sendTransaction({from: addresses[7], to:this.protocolContract.address, value: web3.toWei(1, 'ether'), gasLimit: 21000, gasPrice: 20000000000})
    } catch (e) {
      errr = true
    }
    assert.isTrue(errr, 'Protocol contract should reject ETH transfer')
    assert.isTrue(web3.toDecimal(web3.eth.getBalance(this.protocolContract.address)) === 0, `protocol contract's initial balance should be 0 ether`)
  });

  it("escape_hatch_token should be called only by owner", async function() {
    assert.isTrue(await this.protocolContract.owner() === addresses[0], 'protocol owner is not the first address');
    let errr = false
    try {
      await this.protocolContract.escape_hatch_token(this.BorrowToken.address, {from:addresses[7]});
    } catch (e) {
      errr = true
    }
    assert.isTrue(errr, 'a non-owner should not able to call escape_hatch_token')
    errr = false
    try {
      await this.protocolContract.escape_hatch_token(this.BorrowToken.address, {from:addresses[0]});
    } catch (e) {
      errr = true
    }
    assert.isTrue(!errr, 'owner is not not able to call escape_hatch_token')
  });

  it("tokens should be wihdrawable under an escape-hatch condition", async function() {
    let maliciousUserAddress = addresses[7]
    let maliciousToken = await ERC20.new("Test Yet Another Token", "TYT", 18, 2, {from: maliciousUserAddress});
    let tokenBalance = await maliciousToken.balanceOf(maliciousUserAddress)
    assert.isTrue(tokenBalance.toString() === "2000000000000000000", `maliciousUserAddress should have a token balance of 2 TYT`)
    tx = maliciousToken.transfer(this.protocolContract.address, web3._extend.utils.toWei('2', 'ether'), {from: maliciousUserAddress})
    await mineTx(tx);
    tokenBalance = await maliciousToken.balanceOf(maliciousUserAddress)
    assert.isTrue(tokenBalance.toString() === "0", `maliciousUserAddress should have a token balance of 0 TYT`)
    tokenBalance = await maliciousToken.balanceOf(this.protocolContract.address)
    assert.isTrue(tokenBalance.toString() === "2000000000000000000", `protocolContract should have a token balance of 2 TYT`)
    tokenBalance = await maliciousToken.balanceOf(addresses[0])
    assert.isTrue(tokenBalance.toString() === "0", `protocolContract owner should have a token balance of 0 TYT`)
    tx = this.protocolContract.escape_hatch_token(maliciousToken.address, {from: addresses[0]})
    await mineTx(tx);
    tokenBalance = await maliciousToken.balanceOf(maliciousUserAddress)
    assert.isTrue(tokenBalance.toString() === "0", `maliciousUserAddress should have a token balance of 0 TYT`)
    tokenBalance = await maliciousToken.balanceOf(this.protocolContract.address)
    assert.isTrue(tokenBalance.toString() === "0", `protocolContract should have a token balance of 0 TYT`)
    tokenBalance = await maliciousToken.balanceOf(addresses[0])
    assert.isTrue(tokenBalance.toString() === "2000000000000000000", `protocolContract owner should have a token balance of 2 TYT`)
  });

});
