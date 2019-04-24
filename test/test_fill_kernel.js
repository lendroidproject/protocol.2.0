// helpers
const mineTx = require("./helpers/mineTx.js");
const saltGenerator = require("./helpers/saltGenerator.js");
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
    this.ZERO_ADDRESS = 0x0000000000000000000000000000000000000000;
    this.protocolToken = await ERC20.new("Lendroid Support Token", "LST", 18, 12000000000);
    this.LendToken = await ERC20.new("Test Lend Token", "TLT", 18, 1000000000);
    this.BorrowToken = await ERC20.new("Test Borrow Token", "TBT", 18, 1000000000);
    let KERNEL_TEMPLATE = await KernelTemplate.new(),
      POSITION_TEMPLATE = await PositionTemplate.new();
    this.protocolContract = await Protocol.new(this.protocolToken.address, KERNEL_TEMPLATE.address, POSITION_TEMPLATE.address);
    let tx = await this.protocolContract.set_token_support(this.LendToken.address, true, {from:addresses[0]});
    await mineTx(tx);
    tx = await this.protocolContract.set_token_support(this.BorrowToken.address, true, {from:addresses[0]});
    await mineTx(tx);
    this.lender = addresses[1];
    this.borrower = addresses[2];
    this.relayer = addresses[3];
    this.wrangler = addresses[4];
    //// kernel terms
    // uint256 values
    this.kernel_daily_interest_rate = web3._extend.utils.toWei('0.08', 'ether')
    // timedelta values
    this.kernel_position_duration_in_seconds = 2 * 60 * 60 * 24
    this.wrangler_approval_duration_in_seconds = 5 * 60
    // wei values
    this.kernel_lending_currency_maximum_value = web3._extend.utils.toWei('40', 'ether')
    this.kernel_relayer_fee = web3._extend.utils.toWei('10', 'ether')
    this.kernel_monitoring_fee = web3._extend.utils.toWei('10', 'ether')
    this.kernel_rollover_fee = web3._extend.utils.toWei('10', 'ether')
    this.kernel_closure_fee = web3._extend.utils.toWei('10', 'ether')
    // timestamp values
    this.kernel_expires_at = web3.eth.getBlock(web3.eth.blockNumber).timestamp + 86400*2
    // bytes32 values
    this.kernel_creator_salt = `0x${saltGenerator()}`
    // position terms
    this.position_lending_currency_fill_value = web3._extend.utils.toWei('1', 'ether')
    this.position_borrow_currency_fill_value = web3._extend.utils.toWei('0.1', 'ether')
    this.position_lending_currency_owed_value = web3._extend.utils.toWei('1.0016', 'ether')
  });


  it("fill_kernel should work as expected", async function() {
    // setup
    // set allowance from lender to protocol contract for relayer_fee + monitoring_fee
    tx = this.protocolToken.mint(this.lender, web3._extend.utils.toWei('100', 'ether'), {from: addresses[0]})
    await mineTx(tx);
    tx = this.protocolToken.approve(this.protocolContract.address, web3._extend.utils.toWei('100', 'ether'), {from: this.lender})
    await mineTx(tx);
    // set allowance from lender to protocol contract for loan transfer
    tx = this.LendToken.mint(this.lender, web3._extend.utils.toWei('40', 'ether'), {from: addresses[0]})
    await mineTx(tx);
    tx = this.LendToken.approve(this.protocolContract.address, web3._extend.utils.toWei('40', 'ether'), {from: this.lender})
    await mineTx(tx);
    // set allowance from borrower to protocol contract for collateral transfer
    tx = this.BorrowToken.mint(this.borrower, web3._extend.utils.toWei('5', 'ether'), {from: addresses[0]})
    await mineTx(tx);
    tx = this.BorrowToken.approve(this.protocolContract.address, web3._extend.utils.toWei('5', 'ether'), {from: this.borrower})
    await mineTx(tx);

    // Approve wrangler as protocol owner
    tx = this.protocolContract.set_wrangler_status(this.wrangler, true, {from:addresses[0]});
    await mineTx(tx);
    // position_index check
    let last_position_index = await this.protocolContract.last_position_index()
    assert.isTrue(last_position_index.toString() === '0', 'last_position_index should be 0')
    // lender check
    let lenderPositionCounts = await this.protocolContract.position_counts(this.lender);
    let lenderBorrowPositionsCount = lenderPositionCounts[0];
    let lenderLendPositionsCount = lenderPositionCounts[1];
    assert.isTrue(lenderBorrowPositionsCount.toString() === '0', "lender's borrow position count should be 0");
    assert.isTrue(lenderLendPositionsCount.toString() === '0', "lender's lend position count should be 0");
    // borrower check
    let borrowerPositionCounts = await this.protocolContract.position_counts(this.borrower);
    let borrowerBorrowPositionsCount = borrowerPositionCounts[0];
    let borrowerLendPositionsCount = borrowerPositionCounts[1];
    assert.isTrue(borrowerBorrowPositionsCount.toString() === '0', "borrower's borrow position count should be 0");
    assert.isTrue(borrowerLendPositionsCount.toString() === '0', "borrower's lend position count should be 0");
    // balances check
    let positionContractBorrowTokenBalance;
    let borrowerLendTokenBalance = await this.LendToken.balanceOf(this.borrower);
    assert.isTrue(borrowerLendTokenBalance.toString() === '0', "borrower's LendToken balance should be 0");
    let wranglerProtocolTokenBalance = await this.protocolToken.balanceOf(this.wrangler);
    assert.isTrue(wranglerProtocolTokenBalance.toString() === '0', "wrangler's protocolToken balance should be 0");
    let relayerProtocolTokenBalance = await this.protocolToken.balanceOf(this.relayer);
    assert.isTrue(relayerProtocolTokenBalance.toString() === '0', "relayer's protocolToken balance should be 0");
    // fill kernel and open position
    // Sign kernel hash as lender
    let kernel_hash = await this.protocolContract.kernel_hash(
      [
        this.lender, this.ZERO_ADDRESS, this.relayer, this.wrangler, this.BorrowToken.address, this.LendToken.address
      ],
      [
        this.kernel_lending_currency_maximum_value,
        this.kernel_relayer_fee, this.kernel_monitoring_fee, this.kernel_rollover_fee, this.kernel_closure_fee
      ],
      this.kernel_expires_at, this.kernel_creator_salt,
      this.kernel_daily_interest_rate, this.kernel_position_duration_in_seconds
    )
    this.kernel_creator_signature= web3.eth.sign(this.lender, kernel_hash)
    // Sign position hash as wrangler
    let _nonce = '1';
    this.position_hash = await this.protocolContract.position_hash(
      [
        this.lender, this.lender, this.borrower, this.relayer, this.wrangler, this.BorrowToken.address, this.LendToken.address
      ],
      [
        this.position_borrow_currency_fill_value, this.kernel_lending_currency_maximum_value,
        this.kernel_relayer_fee, this.kernel_monitoring_fee, this.kernel_rollover_fee, this.kernel_closure_fee,
        this.position_lending_currency_fill_value
      ],
      this.position_lending_currency_owed_value,
      _nonce
    )
    let _wrangler_approval_expiry_timestamp = web3.eth.getBlock(web3.eth.blockNumber).timestamp + this.wrangler_approval_duration_in_seconds
    let _wrangler_signature = web3.eth.sign(this.wrangler, this.position_hash)
    // prepare inputs
    let _is_creator_lender = true;
    // test pre-call
    let _kernel_amount_filled = await this.protocolContract.kernels_filled(kernel_hash);
    assert.isTrue(_kernel_amount_filled.toString() === '0');
    let _kernel_amount_cancelled = await this.protocolContract.kernels_cancelled(kernel_hash);
    assert.isTrue(_kernel_amount_cancelled.toString() === '0');
    // do call
    tx = await this.protocolContract.open_position(
      [
        this.lender, this.borrower, this.relayer, this.wrangler, this.BorrowToken.address, this.LendToken.address
      ],
      [
        this.position_borrow_currency_fill_value, this.kernel_lending_currency_maximum_value,
        this.kernel_relayer_fee, this.kernel_monitoring_fee, this.kernel_rollover_fee, this.kernel_closure_fee,
        this.position_lending_currency_fill_value
      ],
      _nonce,
      this.kernel_daily_interest_rate,
      _is_creator_lender,
      [
        this.kernel_expires_at, _wrangler_approval_expiry_timestamp
      ],
      this.kernel_position_duration_in_seconds,
      this.kernel_creator_salt,
      this.kernel_creator_signature,
      _wrangler_signature,
      {from: addresses[0]}
    );

    await mineTx(tx);
    // test post-call
    last_position_index = await this.protocolContract.last_position_index()
    assert.isTrue(last_position_index.toString() === '1', 'last_position_index should be 1')
    lenderPositionCounts = await this.protocolContract.position_counts(this.lender);
    lenderBorrowPositionsCount = lenderPositionCounts[0];
    lenderLendPositionsCount = lenderPositionCounts[1];
    assert.isTrue(lenderBorrowPositionsCount.toString() === '0', "lender's borrow position count should be 0");
    assert.isTrue(lenderLendPositionsCount.toString() === '1', "lender's lend position count should be 1");
    borrowerPositionCounts = await this.protocolContract.position_counts(this.borrower);
    borrowerBorrowPositionsCount = borrowerPositionCounts[0];
    borrowerLendPositionsCount = borrowerPositionCounts[1];
    assert.isTrue(borrowerBorrowPositionsCount.toString() === '1', "borrower's borrow position count should be 1");
    assert.isTrue(borrowerLendPositionsCount.toString() === '0', "borrower's lend position count should be 0");
    let positionContractAddress = await this.protocolContract.borrow_positions(this.borrower, borrowerBorrowPositionsCount);
    positionContractBorrowTokenBalance = await this.BorrowToken.balanceOf(positionContractAddress);
    assert.isTrue(positionContractBorrowTokenBalance.toString() === this.position_borrow_currency_fill_value, `protocolContract's BorrowToken balance should be ${this.position_borrow_currency_fill_value}`);
    borrowerLendTokenBalance = await this.LendToken.balanceOf(this.borrower);
    assert.isTrue(borrowerLendTokenBalance.toString() === this.position_lending_currency_fill_value, `borrower's LendToken balance should be ${this.position_lending_currency_fill_value}`);
    wranglerProtocolTokenBalance = await this.protocolToken.balanceOf(this.wrangler);
    assert.isTrue(wranglerProtocolTokenBalance.toString() === this.kernel_monitoring_fee, `wrangler's protocolToken balance should be ${this.kernel_monitoring_fee}`);
    relayerProtocolTokenBalance = await this.protocolToken.balanceOf(this.relayer);
    assert.isTrue(relayerProtocolTokenBalance.toString() === this.kernel_relayer_fee, `relayer's protocolToken balance should be ${this.kernel_relayer_fee}`);
  });
});
