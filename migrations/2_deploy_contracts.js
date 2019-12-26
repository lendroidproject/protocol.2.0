const ERC20 = artifacts.require('ERC20Template1.vyper')
const PriceFeed = artifacts.require('TestPriceFeed.vyper')
const CurrencyDao = artifacts.require('CurrencyDao.vyper')
const InterestPoolDao = artifacts.require('InterestPoolDao.vyper')
const UnderwriterPoolDao = artifacts.require('UnderwriterPoolDao.vyper')
const MarketDao = artifacts.require('MarketDao.vyper')
const ShieldPayoutDao = artifacts.require('ShieldPayoutDao.vyper')
const PoolNameRegistry = artifacts.require('PoolNameRegistryTemplate1.vyper')
const PositionRegistry = artifacts.require('PositionRegistryTemplate1.vyper')
const CurrencyPool = artifacts.require('ERC20TokenPoolTemplate1.vyper')
const InterestPool = artifacts.require('InterestPoolTemplate1.vyper')
const UnderwriterPool = artifacts.require('UnderwriterPoolTemplate1.vyper')
const PriceOracle = artifacts.require('SimplePriceOracleTemplate1.vyper')
const CollateralAuctionCurve = artifacts.require('SimpleCollateralAuctionCurveTemplate1.vyper')
const MultiFungibleToken = artifacts.require('MultiFungibleTokenTemplate1.vyper')

const ProtocolDao = artifacts.require('ProtocolDao.vyper')

module.exports = function(deployer, network, accounts) {
  console.log('Network : ', network)
  const [Deployer, Test1, Test2, Governor, EscapeHatchManager, EscapeHatchTokenHolder] = accounts
  const contracts = {
    Deployer,
    Test1,
    Test2,
    Governor,
    EscapeHatchManager,
    EscapeHatchTokenHolder,
  }
  const getAddr = (...args) =>
    args.map(token => (typeof contracts[token] === 'string' ? contracts[token] : contracts[token].address))

  deployer
    .deploy(ERC20, 'Lendroid Support Token', 'LST', 18, 12000000000)
    .then(function(instance) {
      console.log('LST deployed at: ', instance.address)
      contracts.LST = instance
      instance.transfer(Test1, '100000000000000000000')
      instance.transfer(Test2, '100000000000000000000')
      return deployer.deploy(ERC20, 'Test Lend Token', 'DAI', 18, 1000000)
    })
    .then(function(instance) {
      console.log('DAI deployed at: ', instance.address)
      contracts.DAI = instance
      instance.transfer(Test1, '100000000000000000000')
      instance.transfer(Test2, '100000000000000000000')
      return deployer.deploy(ERC20, 'Test Borrow Token', 'WETH', 18, 1000000)
    })
    .then(function(instance) {
      console.log('WETH deployed at: ', instance.address)
      contracts.WETH = instance
      instance.transfer(Test1, '100000000000000000000')
      instance.transfer(Test2, '100000000000000000000')
      return deployer.deploy(PriceFeed)
    })
    .then(function(instance) {
      console.log('PriceFeed deployed at: ', instance.address)
      contracts.PriceFeed = instance
      return deployer.deploy(CurrencyDao)
    })
    .then(function(instance) {
      console.log('CurrencyDao deployed at: ', instance.address)
      contracts.CurrencyDao = instance
      return deployer.deploy(InterestPoolDao)
    })
    .then(function(instance) {
      console.log('InterestPoolDao deployed at: ', instance.address)
      contracts.InterestPoolDao = instance
      return deployer.deploy(UnderwriterPoolDao)
    })
    .then(function(instance) {
      console.log('UnderwriterPoolDao deployed at: ', instance.address)
      contracts.UnderwriterPoolDao = instance
      return deployer.deploy(MarketDao)
    })
    .then(function(instance) {
      console.log('MarketDao deployed at: ', instance.address)
      contracts.MarketDao = instance
      return deployer.deploy(ShieldPayoutDao)
    })
    .then(function(instance) {
      console.log('ShieldPayoutDao deployed at: ', instance.address)
      contracts.ShieldPayoutDao = instance
      return deployer.deploy(PoolNameRegistry)
    })
    .then(function(instance) {
      console.log('PoolNameRegistry deployed at: ', instance.address)
      contracts.PoolNameRegistry = instance
      return deployer.deploy(PositionRegistry)
    })
    .then(function(instance) {
      console.log('PositionRegistry deployed at: ', instance.address)
      contracts.PositionRegistry = instance
      return deployer.deploy(CurrencyPool)
    })
    .then(function(instance) {
      console.log('CurrencyPool deployed at: ', instance.address)
      contracts.CurrencyPool = instance
      return deployer.deploy(InterestPool)
    })
    .then(function(instance) {
      console.log('InterestPool deployed at: ', instance.address)
      contracts.InterestPool = instance
      return deployer.deploy(UnderwriterPool)
    })
    .then(function(instance) {
      console.log('UnderwriterPool deployed at: ', instance.address)
      contracts.UnderwriterPool = instance
      return deployer.deploy(PriceOracle, ...getAddr('DAI', 'WETH', 'PriceFeed'))
    })
    .then(function(instance) {
      console.log('PriceOracle deployed at: ', instance.address)
      contracts.PriceOracle = instance
      return deployer.deploy(CollateralAuctionCurve)
    })
    .then(function(instance) {
      console.log('CollateralAuctionCurve deployed at: ', instance.address)
      contracts.CollateralAuctionCurve = instance
      return deployer.deploy(ERC20, '', '', 0, 0)
    })
    .then(function(instance) {
      console.log('ERC20 deployed at: ', instance.address)
      contracts.ERC20 = instance
      return deployer.deploy(MultiFungibleToken)
    })
    .then(function(instance) {
      console.log('MultiFungibleToken deployed at: ', instance.address)
      contracts.MultiFungibleToken = instance
      return deployer.deploy(
        ProtocolDao,
        ...getAddr(
          'LST',
          'Governor',
          'EscapeHatchManager',
          'EscapeHatchTokenHolder',
          'CurrencyDao',
          'InterestPoolDao',
          'UnderwriterPoolDao',
          'MarketDao',
          'ShieldPayoutDao',
          'PoolNameRegistry',
          'PositionRegistry',
          'CurrencyPool',
          'InterestPool',
          'UnderwriterPool',
          'PriceOracle',
          'CollateralAuctionCurve',
          'ERC20',
          'MultiFungibleToken'
        )
      )
    })
    .then(function(instance) {
      console.log('ProtocolDao deployed at: ', instance.address)
      contracts.ProtocolDao = instance
      return contracts.ProtocolDao.initialize_currency_dao({ from: Deployer })
    })
    .then(function(result) {
      console.log('initialize_currency_dao result: ', result)
      return contracts.ProtocolDao.initialize_interest_pool_dao({ from: Deployer })
    })
    .then(function(result) {
      console.log('initialize_interest_pool_dao result: ', result)
      return contracts.ProtocolDao.initialize_underwriter_pool_dao({ from: Deployer })
    })
    .then(function(result) {
      console.log('initialize_underwriter_pool_dao result: ', result)
      return contracts.ProtocolDao.initialize_pool_name_registry(100000000, { from: Deployer })
    })
    .then(function(result) {
      console.log('initialize_pool_name_registry result: ', result)
      return contracts.ProtocolDao.initialize_position_registry({ from: Deployer })
    })
    .then(function(result) {
      console.log('initialize_position_registry result: ', result)
      return contracts.ProtocolDao.initialize_market_dao({ from: Deployer })
    })
    .then(function(result) {
      console.log('initialize_market_dao result: ', result)
      return contracts.ProtocolDao.initialize_shield_payout_dao({ from: Deployer })
    })
    .then(function(result) {
      console.log('initialize_shield_payout_dao result: ', result)
      return contracts.ProtocolDao.set_token_support(contracts.DAI.address, true, { from: Governor })
    })
    .then(function(result) {
      console.log('DAI token support: ', result)

      const addresses = {}
      Object.keys(contracts).forEach(
        token => (addresses[token] = typeof contracts[token] === 'string' ? contracts[token] : contracts[token].address)
      )
      console.log(addresses)
    })
}
