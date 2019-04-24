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
    this.wrangler = addresses[4];
  });


  it("set_wrangler_status should be called only by owner", async function() {
    assert.isTrue(await this.protocolContract.owner() === addresses[0], 'protocol owner is not the first address');
    let errr = false
    try {
      await this.protocolContract.set_wrangler_status(this.wrangler, true, {from:addresses[7]});
    } catch (e) {
      errr = true
    }
    assert.isTrue(errr, 'a non-owner should not able to set the position_threshold value')
    errr = false
    try {
      await this.protocolContract.set_wrangler_status(this.wrangler, true, {from:addresses[0]});
    } catch (e) {
      errr = true
    }
    assert.isTrue(!errr, 'owner is not not able to set the wrangler activation status')
  });


  it("set_wrangler_status should allow owner to activate / deactivate wrangler status", async function() {
    let wrangler_status = await this.protocolContract.wranglers(this.wrangler);
    assert.isTrue(!wrangler_status, 'wrangler should have been deactivated');
    await this.protocolContract.set_wrangler_status(this.wrangler, true, {from:addresses[0]});
    wrangler_status = await this.protocolContract.wranglers(this.wrangler);
    assert.isTrue(wrangler_status, 'wrangler should have been activated');
    await this.protocolContract.set_wrangler_status(this.wrangler, false, {from:addresses[0]});
    wrangler_status = await this.protocolContract.wranglers(this.wrangler);
    assert.isTrue(!wrangler_status, 'wrangler should have been deactivated');
  });


  it("set_token_support should be called only by owner", async function() {
    assert.isTrue(await this.protocolContract.owner() === addresses[0], 'protocol owner is not the first address');
    let errr = false
    try {
      await this.protocolContract.set_token_support(this.LendToken.address, true, {from:addresses[7]});
    } catch (e) {
      errr = true
    }
    assert.isTrue(errr, 'a non-owner should not able to specify token support')
    errr = false
    try {
      await this.protocolContract.set_token_support(this.LendToken.address, true, {from:addresses[0]});
    } catch (e) {
      errr = true
    }
    assert.isTrue(!errr, 'owner is not not able to specify token support')
  });


  it("set_token_support should allow owner to activate / deactivate tokens", async function() {
    let is_token_supported = await this.protocolContract.supported_tokens(this.LendToken.address);
    assert.isTrue(!is_token_supported, 'LendToken should have NOT been supported');
    await this.protocolContract.set_token_support(this.LendToken.address, true, {from:addresses[0]});
    is_token_supported = await this.protocolContract.supported_tokens(this.LendToken.address);
    assert.isTrue(is_token_supported, 'LendToken should have been supported');
    await this.protocolContract.set_token_support(this.LendToken.address, false, {from:addresses[0]});
    is_token_supported = await this.protocolContract.supported_tokens(this.LendToken.address);
    assert.isTrue(!is_token_supported, 'LendToken should have NOT been supported');
  });

  it("set_token_support should not accept non-contract addresses", async function() {
    let errr = false
    try {
      await this.protocolContract.set_token_support(addresses[7], true, {from:addresses[0]});
    } catch (e) {
      errr = true
    }
    assert.isTrue(errr, 'a non-contract token address should be rejected')
    errr = false
    try {
      await this.protocolContract.set_token_support(this.LendToken.address, true, {from:addresses[0]});
    } catch (e) {
      errr = true
    }
    assert.isTrue(!errr, 'owner should be able to set_token_support for Lend token')
  });
});
