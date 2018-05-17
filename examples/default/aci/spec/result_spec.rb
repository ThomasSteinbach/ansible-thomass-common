describe package('python') do
  it { should be_installed }
end

describe package('python-httplib2') do
  it { should be_installed }
end

# Timezone should be Central Europe Time (CET)
describe command('date') do
  its(:stdout) { should match 'CES?T' }
end
