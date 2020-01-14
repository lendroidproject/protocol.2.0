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
const LERC20 = artifacts.require('LERC20Template1.vyper')
const ERC20PoolToken = artifacts.require('ERC20PoolTokenTemplate1.vyper')

const ProtocolDao = artifacts.require('ProtocolDao.vyper')

const monthNames = [
  ['F', 'Jan'],
  ['G', 'Feb'],
  ['H', 'Mar'],
  ['J', 'Apr'],
  ['K', 'May'],
  ['M', 'Jun'],
  ['N', 'Jul'],
  ['Q', 'Aug'],
  ['U', 'Sep'],
  ['V', 'Oct'],
  ['X', 'Nov'],
  ['Z', 'Dec'],
]

const lastWeekdayOfEachMonths = (years, { weekday = 4, from = 0 } = {}) => {
  const lastDay = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  const weekdays = []
  weekdays.match = {}
  for (const year of years) {
    const date = new Date(Date.UTC(year, 0, 1, 12))
    if (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) {
      lastDay[2] = 29
    }
    for (let m = from; m < from + 12; m += 1) {
      const month = m % 12
      const y = year + Math.floor(month / 12)
      const ySuf = y.toString().substr(-2)
      date.setFullYear(y, month % 12, lastDay[month % 12])
      date.setDate(date.getDate() - ((date.getDay() + (7 - weekday)) % 7))
      const name = monthNames[month][0] + ySuf
      const timestamp = Math.round(date.getTime() / 1000)
      const data = {
        name,
        timestamp,
        fullName: `${monthNames[month][1]} ${y}`,
        date: date.toISOString().substring(0, 10),
      }
      weekdays.push(data)
      weekdays.match[name] = timestamp
      weekdays.match[timestamp] = name
    }
  }
  return weekdays
}

const expiries = lastWeekdayOfEachMonths([new Date().getFullYear()])

const toWei = val => `${val}000000000000000000`

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
      instance.transfer(Test1, toWei(16750000))
      instance.transfer(Test2, toWei(16750000))
      return deployer.deploy(ERC20, 'Test Lend Token', 'DAI', 18, 1000000)
    })
    .then(function(instance) {
      console.log('DAI deployed at: ', instance.address)
      contracts.DAI = instance
      instance.transfer(Test1, toWei(2500))
      instance.transfer(Test2, toWei(2500))
      return deployer.deploy(ERC20, 'Test Borrow Token', 'WETH', 18, 1000000)
    })
    .then(function(instance) {
      console.log('WETH deployed at: ', instance.address)
      contracts.WETH = instance
      instance.transfer(Test1, toWei(2500))
      instance.transfer(Test2, toWei(2500))
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
      return deployer.deploy(LERC20)
    })
    .then(function(instance) {
      console.log('LERC20 deployed at: ', instance.address)
      contracts.LERC20 = instance
      return deployer.deploy(ERC20PoolToken)
    })
    .then(function(instance) {
      console.log('ERC20PoolToken deployed at: ', instance.address)
      contracts.ERC20PoolToken = instance
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
          'MultiFungibleToken',
          'LERC20',
          'ERC20PoolToken'
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
      return contracts.ProtocolDao.initialize_pool_name_registry(toWei(250000), { from: Deployer })
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
      return contracts.ProtocolDao.set_token_support(contracts.WETH.address, true, { from: Governor })
    })
    .then(function(result) {
      console.log('WETH token support: ', result)
      return contracts.ProtocolDao.set_pool_name_registration_stake_lookup(4, toWei(500000), { from: Governor })
    })
    .then(function(result) {
      console.log('Reg Stake 4: ', result)
      return contracts.ProtocolDao.set_pool_name_registration_stake_lookup(3, toWei(1000000), { from: Governor })
    })
    .then(function(result) {
      console.log('Reg Stake 3: ', result)
      return contracts.ProtocolDao.set_pool_name_registration_stake_lookup(2, toWei(5000000), { from: Governor })
    })
    .then(function(result) {
      console.log('Reg Stake 2: ', result)
      return contracts.ProtocolDao.set_pool_name_registration_stake_lookup(1, toWei(10000000), { from: Governor })
    })
    .then(function(result) {
      console.log('Reg Stake 1: ', result)
      return contracts.ProtocolDao.set_minimum_mft_fee(2, toWei(250000), { from: Governor })
    })
    .then(function(result) {
      console.log('InterestPool - minimum_mft_fee: ', result)
      return contracts.ProtocolDao.set_minimum_mft_fee(3, toWei(250000), { from: Governor })
    })
    .then(function(result) {
      console.log('UnderwriterPool - minimum_mft_fee: ', result)
      return contracts.ProtocolDao.set_fee_multiplier_per_mft_count(2, '0', toWei(250), { from: Governor })
    })
    .then(function(result) {
      console.log('InterestPool - fee_multiplier_per_mft_count: ', result)
      return contracts.ProtocolDao.set_fee_multiplier_per_mft_count(3, '0', toWei(250), { from: Governor })
    })
    .then(function(result) {
      console.log('UnderwriterPool - fee_multiplier_per_mft_count: ', result)
      return Promise.all(
        expiries.map(
          ({ timestamp, name }) =>
            new Promise((resolve, reject) =>
              contracts.ProtocolDao.set_expiry_support(timestamp, name, true, { from: Governor })
                .then(() => resolve({ [name]: timestamp }))
                .catch(e => reject(e))
            )
        )
      )
    })
    .then(function(results) {
      console.log('Expiries support: ', results)
      return Promise.all([
        ...expiries.map(
          ({ timestamp, name }) =>
            new Promise((resolve, reject) =>
              contracts.ProtocolDao.set_maximum_liability_for_loan_market(
                contracts.DAI.address,
                timestamp,
                contracts.WETH.address,
                toWei(1000000),
                { from: Governor }
              )
                .then(() => resolve({ [`DAI-WETH-${name}`]: timestamp }))
                .catch(e => reject(e))
            )
        ),
        ...expiries.map(
          ({ timestamp, name }) =>
            new Promise((resolve, reject) =>
              contracts.ProtocolDao.set_maximum_liability_for_loan_market(
                contracts.WETH.address,
                timestamp,
                contracts.DAI.address,
                toWei(1000000),
                { from: Governor }
              )
                .then(() => resolve({ [`WETH-DAI-${name}`]: timestamp }))
                .catch(e => reject(e))
            )
        ),
      ])
    })
    .then(function(results) {
      console.log('maximum_liability_for_loan_market: ', results)

      const addresses = {}
      Object.keys(contracts).forEach(
        token => (addresses[token] = typeof contracts[token] === 'string' ? contracts[token] : contracts[token].address)
      )
      console.log(addresses)
    })
}
