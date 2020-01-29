export default function partial(f) {
    let args = Array.prototype.slice.call(arguments, 1);
    return function() {
        let remainingArgs = Array.prototype.slice.call(arguments);
        return f.apply(null, args.concat(remainingArgs));
    };
}
