for i in $(find . -type f -name "xy_[0-9]*"); do
    plotname=${i/xy/plot}
    plotname=${plotname/dat/png}
    echo "python find_regime_change.py ${i} --plotname ${plotname}"
    python find_regime_change.py ${i} --plotname ${plotname}
done
